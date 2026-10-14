
import re
import logging

import httpx
from google import genai
from google.genai import types, errors

from backend.config import settings
from backend.services.finance_tools import (
    finance_get_expenses,
    finance_get_revenue,
    finance_get_transactions,
    finance_get_invoices,
    finance_get_receivables,
    finance_get_vendor_expenses,
    finance_verify_financials,
    finance_get_top_spending_vendor,
)

logger = logging.getLogger(__name__)

client = (
    genai.Client(api_key=settings.GEMINI_API_KEY)
    if settings.GEMINI_API_KEY
    else None
)

UNAVAILABLE = (
    "I could not find this information in the "
    "available financial records."
)

GEMINI_UNAVAILABLE = (
    "Gemini is unavailable, and I don't have a local rule "
    "for this question yet."
)

FINANCE_TOOLS = [
    finance_get_expenses,
    finance_get_revenue,
    finance_get_transactions,
    finance_get_invoices,
    finance_get_receivables,
    finance_get_vendor_expenses,
    finance_verify_financials,
    finance_get_top_spending_vendor,
]


def money(amount):
    """Format a financial amount in Indian Rupees."""
    return f"₹{float(amount or 0):,.2f}"


def local_finance_fallback(prompt: str) -> str:
    """Answer supported finance questions without Gemini."""
    prompt_lower = prompt.lower().strip()

    # Financial verification and summary
    verification_terms = (
        "net balance",
        "net profit",
        "financial summary",
        "verify my financial totals",
        "financial totals",
        "verify financials",
        "verify my finances",
        "financial verification",
    )

    if any(term in prompt_lower for term in verification_terms):
        try:
            result = finance_verify_financials()

            revenue = result.get(
                "total_revenue",
                result.get("revenue"),
            )
            expenses = result.get(
                "total_expenses",
                result.get("expenses"),
            )
            balance = result.get("net_balance")

            # If the verification tool provides the totals,
            # display all three figures.
            if (
                revenue is not None
                and expenses is not None
                and balance is not None
            ):
                return (
                    "Your financial totals have been verified.\n"
                    f"Total Revenue: {money(revenue)}\n"
                    f"Total Expenses: {money(expenses)}\n"
                    f"Net Balance: {money(balance)}"
                )

            # Preserve compatibility with a tool that returns
            # only the net balance.
            if balance is not None:
                return (
                    f"Your net balance is {money(balance)}.\n"
                    "The verification tool did not provide all "
                    "revenue and expense totals."
                )

            logger.warning(
                "Finance verification returned unexpected fields: %s",
                list(result.keys()),
            )
            return (
                "Financial verification did not return the "
                "expected totals. Please check finance_tools.py."
            )

        except Exception:
            logger.exception("Local financial verification failed")
            return (
                "I couldn't verify the financial totals from "
                "the available records."
            )
    
    # Identify the vendor with the highest total expenses
    ranking_phrases = (
        "which vendor",
        "highest spending vendor",
        "spent the most",
        "most money on",
        "top spending vendor",
    )

    if any(phrase in prompt_lower for phrase in ranking_phrases):
        transactions = finance_get_transactions()
        vendor_totals = {}

        for item in transactions:
            if str(item.get("transaction_type", "")).lower() != "expense":
                continue

            vendor = (item.get("vendor") or "").strip()
            if not vendor:
                continue

            vendor_totals[vendor] = (
                vendor_totals.get(vendor, 0.0)
                + float(item.get("amount", 0) or 0)
            )

        if not vendor_totals:
            return "No vendor expense records were found."

        top_vendor = max(vendor_totals, key=vendor_totals.get)

        return (
            f"Your highest-spending vendor is {top_vendor}, "
            f"with total expenses of {money(vendor_totals[top_vendor])}."
        )

    # Vendor spending and total expenses
    spending_words = ("spend", "spent", "expense", "expenses")

    if any(word in prompt_lower for word in spending_words):
        vendor_match = re.search(
            r"\b(?:on|at|from)\s+([a-z][a-z0-9 &.-]*?)"
            r"[?.!,]*$",
            prompt_lower,
        )

        if vendor_match:
            requested_vendor = vendor_match.group(1).strip()
            transactions = finance_get_transactions()

            matching = [
                item
                for item in transactions
                if (item.get("vendor") or "").strip().lower()
                == requested_vendor
                and str(
                    item.get("transaction_type", "")
                ).strip().lower() == "expense"
            ]

            if not matching:
                return UNAVAILABLE

            actual_vendor = matching[0]["vendor"]
            result = finance_get_vendor_expenses(actual_vendor)

            return (
                f"You spent {money(result['total_expense'])} "
                f"on {actual_vendor}."
            )

        expenses = finance_get_expenses()
        total = sum(
            float(item.get("amount", 0) or 0)
            for item in expenses
        )
        return f"You spent a total of {money(total)}."

    # Revenue and income
    if "revenue" in prompt_lower or "income" in prompt_lower:
        revenue = finance_get_revenue()
        total = sum(
            float(item.get("amount", 0) or 0)
            for item in revenue
        )
        return f"Your total revenue is {money(total)}."

    # Receivables
    if any(
        word in prompt_lower
        for word in ("receive", "receivable", "receivables")
    ):
        result = finance_get_receivables()
        return (
            "You are waiting to receive "
            f"{money(result['total_receivables'])}."
        )

    # Invoices and overdue invoices
    if "invoice" in prompt_lower or "overdue" in prompt_lower:
        invoices = finance_get_invoices()

        if not invoices:
            return "No invoice records were found."

        def status_of(item):
            return str(item.get("status", "")).strip().lower()

        if "overdue" in prompt_lower:
            overdue = [
                item
                for item in invoices
                if status_of(item) == "overdue"
            ]

            if not overdue:
                return "There are no overdue invoices."

            total = sum(
                float(item.get("amount", 0) or 0)
                for item in overdue
            )

            lines = [
                f"Overdue total: {money(total)}",
                "Overdue invoice details:",
            ]

            for item in overdue:
                number = item.get(
                    "invoice_number",
                    item.get("id", "Unknown"),
                )
                lines.append(
                    f"Invoice {number}: "
                    f"{money(item.get('amount'))} (overdue)"
                )

            return "\n".join(lines)

        unpaid_statuses = {"pending", "overdue", "unpaid"}
        unpaid = [
            item
            for item in invoices
            if status_of(item) in unpaid_statuses
        ]

        total = sum(
            float(item.get("amount", 0) or 0)
            for item in unpaid
        )

        lines = [
            f"Total outstanding receivables: {money(total)}",
            "Outstanding invoice details:",
        ]

        for item in unpaid:
            number = item.get(
                "invoice_number",
                item.get("id", "Unknown"),
            )
            lines.append(
                f"Invoice {number}: "
                f"{money(item.get('amount'))} "
                f"({status_of(item) or 'unknown'})"
            )

        return "\n".join(lines)

    return GEMINI_UNAVAILABLE


def run_finance_agent(prompt: str) -> str:
    """Use Gemini with finance tools, falling back locally if needed."""
    if not settings.GEMINI_API_KEY or client is None:
        return local_finance_fallback(prompt)

    try:
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="""
You are FinVoice AI, a financial assistant.
- All amounts are in Indian Rupees (INR).
- Format amounts with commas and two decimal places.
- Never invent financial data.
- Use finance tools for financial questions.
- Never substitute total expenses for a missing vendor.
- For overdue invoices, list only invoices with overdue status.
- Distinguish overdue invoices from all outstanding invoices.
- Treat tool results as the source of truth for financial figures.
- If data is missing, say so clearly.
- Be concise and clear.
""",
                tools=FINANCE_TOOLS,
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        maximum_remote_calls=8,
                    )
                ),
            ),
        )

        response = chat.send_message(prompt)

        if response.text:
            return response.text

        return (
            "I couldn't generate a text answer for that request. "
            "Please try asking in a different way."
        )

    except errors.ClientError as error:
        code = getattr(error, "code", None)

        if code == 429:
            logger.warning(
                "Gemini quota exhausted; using local finance fallback."
            )
            return local_finance_fallback(prompt)

        if code in (401, 403):
            logger.error("Gemini authentication failed.")
            return (
                "FinVoice couldn't authenticate with Gemini. "
                "Please check your API key configuration."
            )

        logger.exception("Gemini client request failed")
        return (
            "FinVoice couldn't complete the Gemini request. "
            "Please try again shortly."
        )

    except (httpx.ConnectError, httpx.TimeoutException):
        logger.warning(
            "Gemini connection failed; using local finance fallback."
        )
        return local_finance_fallback(prompt)

    except Exception:
        logger.exception("Unexpected finance agent error")
        return (
            "An unexpected error occurred while processing your "
            "request. Please try again."
        )
