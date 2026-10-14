from sqlalchemy import text
from backend.database import engine


def get_transactions():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM transactions")
        )

        return [dict(row) for row in result.mappings()]


def get_expenses():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM transactions
                WHERE transaction_type = 'expense'
            """)
        )

        return [dict(row) for row in result.mappings()]


def get_revenue():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM transactions
                WHERE transaction_type = 'revenue'
            """)
        )

        return [dict(row) for row in result.mappings()]


def get_summary():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    SUM(CASE
                        WHEN transaction_type = 'revenue'
                        THEN amount ELSE 0
                    END) AS total_revenue,

                    SUM(CASE
                        WHEN transaction_type = 'expense'
                        THEN amount ELSE 0
                    END) AS total_expenses
                FROM transactions
            """)
        )

        row = result.mappings().first()

        total_revenue = row["total_revenue"] or 0
        total_expenses = row["total_expenses"] or 0

        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_balance": total_revenue - total_expenses
        }


def get_invoices():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM invoices")
        )

        return [dict(row) for row in result.mappings()]


def get_receivables():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    SUM(amount) AS total_receivables
                FROM invoices
                WHERE status IN ('pending', 'overdue')
            """)
        )

        row = result.mappings().first()

        return {
            "total_receivables": row["total_receivables"] or 0
        }


def get_vendor_expenses(vendor: str):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    vendor,
                    SUM(amount) AS total_expense
                FROM transactions
                WHERE vendor = :vendor
                  AND transaction_type = 'expense'
                GROUP BY vendor
            """),
            {"vendor": vendor}
        )

        row = result.mappings().first()

        if row is None:
            return {
                "vendor": vendor,
                "total_expense": 0
            }

        return {
            "vendor": row["vendor"],
            "total_expense": row["total_expense"]
        }

def get_financial_verification():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type = 'revenue'
                                THEN amount
                                ELSE 0
                            END
                        ), 0
                    ) AS total_revenue,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type = 'expense'
                                THEN amount
                                ELSE 0
                            END
                        ), 0
                    ) AS total_expenses
                FROM transactions
            """)
        )

        row = result.mappings().first()

        revenue = float(row["total_revenue"])
        expenses = float(row["total_expenses"])

        return {
            "total_revenue": revenue,
            "total_expenses": expenses,
            "net_balance": revenue - expenses
        }