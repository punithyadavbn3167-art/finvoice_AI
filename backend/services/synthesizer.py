
import re


# Matches amounts such as:
# ₹3,700.50, ₹800,000, Rs. 15,00,000
AMOUNT_PATTERN = r"(?:₹|Rs\.?)\s*([\d,]+(?:\.\d{1,2})?)"


def extract_amount(text: str):
    """Extract the most relevant monetary amount from an agent response."""

    if not text:
        return None

    # Prefer amounts explicitly associated with the requested metric.
    priority_patterns = [
        rf"(?:total\s+expenses|current\s+expenses)"
        rf"\s*:\s*{AMOUNT_PATTERN}",
        rf"\bexpenses\b\s*:\s*{AMOUNT_PATTERN}",
        rf"\bspent\b.*?{AMOUNT_PATTERN}",
        rf"\brevenue\b\s*:\s*{AMOUNT_PATTERN}",
        rf"\bprofit\b\s*:\s*{AMOUNT_PATTERN}",
    ]

    for pattern in priority_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    # Fallback: use the first currency amount if no labelled amount matches.
    match = re.search(AMOUNT_PATTERN, text, flags=re.IGNORECASE)

    if not match:
        return None

    return float(match.group(1).replace(",", ""))


def synthesize_financial_answer(
    finance_answer: str,
    rag_answer: str,
):
    """Combine current database expenses and report expenses."""

    current_expenses = extract_amount(finance_answer)
    report_expenses = extract_amount(rag_answer)

    if current_expenses is None or report_expenses is None:
        return (
            "I could not reliably extract the financial "
            "amounts needed for comparison."
        )

    difference = report_expenses - current_expenses

    return (
        "Based on your current financial records "
        "and the financial report:\n\n"
        f"• Current expenses: ₹{current_expenses:,.2f}\n"
        f"• Report expenses: ₹{report_expenses:,.2f}\n"
        f"• Difference: ₹{difference:,.2f}"
    )