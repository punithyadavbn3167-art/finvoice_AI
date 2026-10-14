
def classify_query(query: str) -> str:
    query_lower = query.lower()

    document_keywords = [
        "report",
        "document",
        "pdf",
        "according to the report",
        "according to the document",
        "previous year",
        "financial report",
    ]

    finance_keywords = [
        "expense",
        "expenses",
        "revenue",
        "spent",
        "spend",
        "amazon",
        "transaction",
        "transactions",
        "invoice",
        "invoices",
        "receive",
        "receivable",
        "receivables",
        "vendor",
        "balance",
        "profit",
        "database",
        "current",
        "summary",
        "financial summary",
    ]

    mixed_indicators = [
        "compare",
        "both",
        "against my current",
        "compare with my database",
        "database and the report",
        "report and the database",
        "database and report",
        "report and database",
    ]

    has_document = any(
        keyword in query_lower
        for keyword in document_keywords
    )

    has_finance = any(
        keyword in query_lower
        for keyword in finance_keywords
    )

    if has_document and has_finance and any(
        indicator in query_lower
        for indicator in mixed_indicators
    ):
        return "mixed"

    if has_document:
        return "rag"

    if has_finance:
        return "finance"

    return "unknown"
