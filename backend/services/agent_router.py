
import re

from backend.services.planner import classify_query
from backend.services.finance_agent import (
    run_finance_agent,
    local_finance_fallback,
)
from backend.rag.rag_agent import run_rag_agent
from backend.services.synthesizer import (
    synthesize_financial_answer,
    extract_amount,
)
from backend.services.verifier import (
    verify_financials,
    verify_expense_amount,
)


def route_query(query: str):
    query_lower = query.lower().strip()
    route = classify_query(query)

    # Route common finance questions to the finance agent
    # if the planner cannot classify them.
    finance_keywords = (
        "revenue",
        "income",
        "expense",
        "expenses",
        "net balance",
        "profit",
        "invoice",
        "overdue",
        "receivable",
        "receivables",
        "vendor",
        "spent",
        "financial totals",
        "verify my financial totals",
        "financial summary",
        "transaction",
        "transactions",
    )

    if route == "unknown" and any(
        keyword in query_lower for keyword in finance_keywords
    ):
        route = "finance"

    asks_receivables = any(
        word in query_lower
        for word in (
            "owe",
            "receivable",
            "receivables",
            "still due",
        )
    )
    asks_overdue = "overdue" in query_lower

    # Handle combined receivables and overdue questions locally.
    if asks_receivables and asks_overdue:
        return local_finance_fallback(query)

    if route == "finance":
        return run_finance_agent(query)

    if route == "rag":
        return run_rag_agent(query)

    if route == "unknown":
        return (
            "I could not determine which agent should handle "
            "this question. Try asking about revenue, expenses, "
            "invoices, transactions, or your financial records."
        )

    if route == "mixed":
        finance_answer = run_finance_agent(
            "What are my current expenses?"
        )
        rag_answer = run_rag_agent(
            "What are the expenses mentioned in the financial report?"
        )

        verification = verify_financials()

        if not verification["verified"]:
            return (
                "Financial verification failed. "
                "The calculated financial values are inconsistent."
            )

        current_expenses = extract_amount(finance_answer)

        if current_expenses is None:
            return (
                "Financial verification failed. "
                "Could not extract the current expense amount."
            )

        expense_verification = verify_expense_amount(
            current_expenses
        )

        if not expense_verification["verified"]:
            return (
                "Financial verification failed. "
                "Current expenses do not match the database."
            )

        report_expenses = extract_amount(rag_answer)

        if report_expenses is None:
            return (
                "Financial verification failed. "
                "Could not extract report expenses."
            )

        expected_difference = abs(
            report_expenses - current_expenses
        )

        synthesized_answer = synthesize_financial_answer(
            finance_answer,
            rag_answer,
        )

        # Accept common currency formats such as ₹1,200.00
        # and INR 1,200.00.
        match = re.search(
            r"^\s*(?:[-•*]\s*)?Difference:\s*"
            r"(?:₹|INR\s*)\s*"
            r"([\d,]+(?:\.\d{1,2})?)\s*$",
            synthesized_answer,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        if not match:
            return (
                "Financial verification failed. "
                "Could not find a valid difference in the answer."
            )

        actual_difference = float(
            match.group(1).replace(",", "")
        )

        if abs(actual_difference - expected_difference) >= 0.005:
            return (
                "Financial verification failed. "
                "The reported expense difference is incorrect."
            )

        return synthesized_answer

    return "Unsupported query route."
