
from backend.services.synthesizer import (
    extract_amount,
    synthesize_financial_answer,
)


def test_extracts_indian_currency_amount():
    amount = extract_amount("Current expenses: \u20b93,700.50")

    assert amount == 3700.50


def test_extracts_amount_with_indian_digit_grouping():
    amount = extract_amount("Expenses: Rs. 8,00,000")

    assert amount == 800000.0


def test_synthesizes_correct_difference():
    answer = synthesize_financial_answer(
        "Current expenses: \u20b93,700.50",
        "Expenses: \u20b98,00,000",
    )

    assert "Current expenses: \u20b93,700.50" in answer
    assert "Report expenses: \u20b9800,000.00" in answer
    assert "Difference: \u20b9796,299.50" in answer


def test_missing_amount_returns_safe_message():
    answer = synthesize_financial_answer(
        "No expense amount available",
        "Expenses: \u20b98,00,000",
    )

    assert "could not reliably extract" in answer.lower()