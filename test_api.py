
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint_returns_routed_answer():
    with patch(
        "backend.main.route_query",
        return_value="You spent ₹3,700.50.",
    ) as mocked_route:
        response = client.post(
            "/chat",
            json={"message": "How much did I spend?"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "response": "You spent ₹3,700.50."
    }
    mocked_route.assert_called_once_with("How much did I spend?")


def test_chat_rejects_missing_message():
    response = client.post("/chat", json={})

    assert response.status_code == 422

def test_chat_rejects_whitespace_message():
    response = client.post(
        "/chat",
        json={"message": "   "},
    )

    assert response.status_code == 422


def test_chat_rejects_message_over_2000_characters():
    response = client.post(
        "/chat",
        json={"message": "a" * 2001},
    )

    assert response.status_code == 422


def test_chat_handles_unexpected_error_safely():
    with patch(
        "backend.main.route_query",
        side_effect=RuntimeError("Sensitive internal error"),
    ):
        response = client.post(
            "/chat",
            json={"message": "Give me my financial summary"},
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected error occurred while processing your message."
    }
    assert "Sensitive internal error" not in response.text

def test_database_error_returns_503():
    from fastapi.testclient import TestClient
    from sqlalchemy.exc import SQLAlchemyError
    from unittest.mock import patch
    from backend.main import app

    client = TestClient(app)

    with patch(
        "backend.main.get_transactions",
        side_effect=SQLAlchemyError("Sensitive database details"),
    ):
        response = client.get("/transactions")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The database is temporarily unavailable. Please try again later."
    }
    assert "Sensitive database details" not in response.text