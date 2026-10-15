
from unittest.mock import patch

from backend.services.agent_router import route_query


def test_finance_query_routes_to_finance_agent():
    with patch(
        "backend.services.agent_router.run_finance_agent",
        return_value="Finance answer",
    ) as agent:
        result = route_query("What are my current expenses?")

    assert result == "Finance answer"
    agent.assert_called_once_with("What are my current expenses?")


def test_rag_query_routes_to_rag_agent():
    with patch(
        "backend.services.agent_router.run_rag_agent",
        return_value="Report answer",
    ) as agent:
        result = route_query("Summarize the financial report")

    assert result == "Report answer"
    agent.assert_called_once_with("Summarize the financial report")


def test_unknown_query_returns_fallback_message():
    with patch(
        "backend.services.agent_router.classify_query",
        return_value="unknown",
    ):
        result = route_query("Tell me something unrelated")

    assert result.startswith(
        "I could not determine which agent should handle this question."
    )


def test_receivables_and_overdue_query_uses_deterministic_fallback():
    query = (
        "How much money do customers still owe me, "
        "and which invoices are overdue?"
    )
    expected = (
        "Total outstanding receivables: Rs. 50,000.00\n"
        "Overdue total: Rs. 32,000.00\n"
        "Invoice details:\n"
        "Invoice INV-001: Rs. 25,000.00 (paid)\n"
        "Invoice INV-002: Rs. 18,000.00 (pending)\n"
        "Invoice INV-003: Rs. 32,000.00 (overdue)"
    )

    with patch(
        "backend.services.agent_router.local_finance_fallback",
        return_value=expected,
    ) as fallback, patch(
        "backend.services.agent_router.run_finance_agent"
    ) as finance_agent:
        result = route_query(query)

    assert result == expected
    fallback.assert_called_once_with(query)
    finance_agent.assert_not_called()


def test_financial_summary_routes_to_finance_agent():
    query = "Give me my financial summary"

    with patch(
        "backend.services.agent_router.run_finance_agent",
        return_value="Financial summary answer",
    ) as agent:
        result = route_query(query)

    assert result == "Financial summary answer"
    agent.assert_called_once_with(query)