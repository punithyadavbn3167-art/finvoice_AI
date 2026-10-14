
from backend.services.verifier import (
    verify_financials,
    verify_expense_amount,
)


def test_financials_are_consistent():
    result = verify_financials()

    assert result["verified"] is True


def test_correct_expense_amount_is_accepted():
    result = verify_expense_amount(3700.50)

    assert result["verified"] is True


def test_incorrect_expense_amount_is_rejected():
    result = verify_expense_amount(9999.99)

    assert result["verified"] is False