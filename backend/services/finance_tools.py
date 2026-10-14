import logging
logger = logging.getLogger(__name__)
from backend.services.finance_service import (
    get_expenses,
    get_revenue,
    get_transactions,
    get_invoices,
    get_receivables,
    get_vendor_expenses,
    get_financial_verification,
)

logger = logging.getLogger(__name__)


def finance_get_expenses():
    logger.info("Finance tool executed: finance_get_expenses")
    expenses = get_expenses()

    return [
        {
            "id": expense["id"],
            "amount": float(expense["amount"]),
            "transaction_type": expense["transaction_type"],
            "description": expense["description"],
            "vendor": expense["vendor"],
            "transaction_date": expense["transaction_date"].isoformat()
        }
        for expense in expenses
    ]


def finance_get_revenue():
    logger.info("Finance tool executed: finance_get_revenue")
    revenue = get_revenue()

    return [
        {
            "id": item["id"],
            "amount": float(item["amount"]),
            "transaction_type": item["transaction_type"],
            "description": item["description"],
            "vendor": item["vendor"],
            "transaction_date": item["transaction_date"].isoformat()
        }
        for item in revenue
    ]


def finance_get_transactions():
    logger.info("Finance tool executed: finance_get_transactions")
    transactions = get_transactions()

    return [
        {
            "id": transaction["id"],
            "amount": float(transaction["amount"]),
            "transaction_type": transaction["transaction_type"],
            "description": transaction["description"],
            "vendor": transaction["vendor"],
            "transaction_date": transaction["transaction_date"].isoformat()
        }
        for transaction in transactions
    ]


def finance_get_invoices():
    logger.info("Finance tool executed: finance_get_invoices")
    invoices = get_invoices()

    return [
        {
            "id": invoice["id"],
            "invoice_number": invoice["invoice_number"],
            "customer": invoice["customer"],
            "amount": float(invoice["amount"]),
            "status": invoice["status"],
            "due_date": invoice["due_date"].isoformat()
                if invoice["due_date"] else None,
            "created_at": invoice["created_at"].isoformat()
                if invoice["created_at"] else None
        }
        for invoice in invoices
    ]


def finance_get_receivables():
    logger.info("Finance tool executed: finance_get_receivables")
    receivables = get_receivables()

    return {
        "total_receivables": float(receivables["total_receivables"])
    }


def finance_get_vendor_expenses(vendor: str):
    logger.info("Finance tool executed: finance_get_vendor_expenses")
    result = get_vendor_expenses(vendor)

    return {
        "vendor": result["vendor"],
        "total_expense": float(result["total_expense"])
    }


def finance_verify_financials():
    logger.info("Finance tool executed: finance_verify_financials")
    return get_financial_verification()



def finance_get_top_spending_vendor():
    """Return the vendor with the highest total recorded expenses."""
    logger.info("Finance tool executed: finance_get_top_spending_vendor")

    transactions = finance_get_transactions()
    vendor_totals = {}

    for item in transactions:
        if str(item.get("transaction_type", "")).lower() != "expense":
            continue

        vendor = (item.get("vendor") or "").strip()
        if not vendor:
            continue

        amount = float(item.get("amount", 0) or 0)
        vendor_totals[vendor] = vendor_totals.get(vendor, 0.0) + amount

    if not vendor_totals:
        return {
            "vendor": None,
            "total_expense": 0.0,
            "message": "No vendor expense records were found."
        }

    top_vendor = max(vendor_totals, key=vendor_totals.get)

    return {
        "vendor": top_vendor,
        "total_expense": round(vendor_totals[top_vendor], 2)
    }
