
import pytest

from backend.services.planner import classify_query


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("How much did I spend?", "finance"),
        ("What is my total revenue?", "finance"),
        ("What does the financial report say?", "rag"),
        (
            "According to the PDF, what was the previous year's revenue?",
            "rag",
        ),
        (
            "Compare my expenses with the expenses in the financial report.",
            "mixed",
        ),
        (
            "What is my current revenue according to the database and the report?",
            "mixed",
        ),
        ("Hello", "unknown"),
    ],
)
def test_classify_query(query, expected):
    assert classify_query(query) == expected
