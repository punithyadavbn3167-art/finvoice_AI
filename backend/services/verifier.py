from backend.services.finance_service import get_financial_verification


def verify_financials():
    data = get_financial_verification()

    revenue = data["total_revenue"]
    expenses = data["total_expenses"]
    net_balance = data["net_balance"]

    calculated_balance = revenue - expenses

    balance_verified = (
        abs(net_balance - calculated_balance) < 0.01
    )

    return {
        "verified": balance_verified,
        "total_revenue": revenue,
        "total_expenses": expenses,
        "net_balance": net_balance,
        "calculated_balance": calculated_balance,
    }


def verify_expense_amount(
    synthesized_expenses: float
):
    data = get_financial_verification()

    database_expenses = data["total_expenses"]

    difference = abs(
        synthesized_expenses - database_expenses
    )

    return {
        "verified": difference < 0.01,
        "synthesized_expenses": synthesized_expenses,
        "database_expenses": database_expenses,
        "difference": difference
    }