from google import genai
from google.genai import types
from google.genai import errors
from backend.config import settings
from backend.services.finance_tools import (
    finance_get_expenses,
    finance_get_revenue,
    finance_get_transactions,
    finance_get_invoices,
    finance_get_receivables,
    finance_get_vendor_expenses,
    finance_verify_financials
)

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def ask_gemini(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def ask_finance_agent(prompt: str):
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""
You are FinVoice AI, a financial assistant.

Rules:
- All financial amounts are in Indian Rupees (INR).
- NEVER use $, USD, or the word dollars.
- Always use the ₹ symbol for monetary values.
- Always format monetary values with commas and two decimal places.
- Example: ₹2,500.00, ₹15,000.00, ₹50,000.00.
- Never invent financial data.
- Use finance tools when the user asks about financial data.
- Base financial answers only on data returned by the tools.
- Be concise and clear.
""",
            tools=[
                finance_get_expenses,
                finance_get_revenue,
                finance_get_transactions,
                finance_get_invoices,
                finance_get_receivables,
                finance_get_vendor_expenses,
                finance_verify_financials,
            ],
        ),
    )

    try:
        response = chat.send_message(prompt)
        return response.text

    except errors.ClientError as e:
        if e.code == 429:
            return local_finance_fallback(prompt)

        raise
    

def local_finance_fallback(prompt: str):
    prompt_lower = prompt.lower()

    if "amazon" in prompt_lower and "spend" in prompt_lower:
        result = finance_get_vendor_expenses("Amazon")

        return (
            f"You spent ₹{result['total_expense']:,.2f} "
            f"on {result['vendor']}."
        )

    if "how much" in prompt_lower and "receive" in prompt_lower:
        result = finance_get_receivables()

        return (
            f"You are waiting to receive "
            f"₹{result['total_receivables']:,.2f}."
        )

    if "expense" in prompt_lower or "spent" in prompt_lower:
        expenses = finance_get_expenses()

        total = sum(item["amount"] for item in expenses)

        return f"Your total expenses are ₹{total:,.2f}."

    return (
        "Gemini is currently unavailable, and I don't have "
        "a local rule for this question yet."
    )
