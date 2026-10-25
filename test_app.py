"""
pytest tests for FinSecure Pay API
Tests both /health and /validate endpoints with multiple scenarios.
"""

from fastapi.testclient import TestClient
from app import app

# TestClient = fake browser that calls your API directly, no server needed
client = TestClient(app)


# ============================================================
# /health endpoint tests
# ============================================================

def test_health_endpoint_returns_200():
    """Health endpoint should return HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_correct_json():
    """Health endpoint should return the expected status and service name."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "finsecure-pay"


# ============================================================
# /validate endpoint — SUCCESS cases
# ============================================================

def test_validate_approves_valid_transaction():
    """A clean, valid transaction should be approved."""
    transaction = {
        "transaction_id": "txn_001",
        "amount": 50.00,
        "currency": "SGD",
        "card_number": "4111111111111111",
        "merchant": "Starbucks"
    }
    response = client.post("/validate", json=transaction)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["transaction_id"] == "txn_001"


def test_validate_accepts_multiple_currencies():
    """Supported currencies (USD, SGD, EUR, GBP) should all be approved."""
    for currency in ["USD", "SGD", "EUR", "GBP"]:
        transaction = {
            "transaction_id": f"txn_{currency}",
            "amount": 100.00,
            "currency": currency,
            "card_number": "4111111111111111",
            "merchant": "Test Merchant"
        }
        response = client.post("/validate", json=transaction)
        assert response.json()["status"] == "approved"


# ============================================================
# /validate endpoint — FAILURE cases
# ============================================================

def test_validate_rejects_zero_amount():
    """Transactions with zero amount should be rejected."""
    transaction = {
        "transaction_id": "txn_zero",
        "amount": 0,
        "currency": "SGD",
        "card_number": "4111111111111111",
        "merchant": "Starbucks"
    }
    response = client.post("/validate", json=transaction)
    assert response.json()["status"] == "rejected"
    assert "greater than zero" in response.json()["reason"]


def test_validate_rejects_amount_over_limit():
    """Transactions over $10,000 should be rejected."""
    transaction = {
        "transaction_id": "txn_big",
        "amount": 15000.00,
        "currency": "SGD",
        "card_number": "4111111111111111",
        "merchant": "Starbucks"
    }
    response = client.post("/validate", json=transaction)
    assert response.json()["status"] == "rejected"
    assert "exceeds maximum" in response.json()["reason"]


def test_validate_rejects_unsupported_currency():
    """Unsupported currencies (e.g., JPY) should be rejected."""
    transaction = {
        "transaction_id": "txn_jpy",
        "amount": 50.00,
        "currency": "JPY",
        "card_number": "4111111111111111",
        "merchant": "Starbucks"
    }
    response = client.post("/validate", json=transaction)
    assert response.json()["status"] == "rejected"
    assert "not supported" in response.json()["reason"]


def test_validate_rejects_invalid_card_number():
    """Card numbers that are too short should be rejected."""
    transaction = {
        "transaction_id": "txn_shortcard",
        "amount": 50.00,
        "currency": "SGD",
        "card_number": "1234",
        "merchant": "Starbucks"
    }
    response = client.post("/validate", json=transaction)
    assert response.json()["status"] == "rejected"
    assert "card number" in response.json()["reason"].lower()


def test_validate_rejects_empty_merchant():
    """Transactions with no merchant should be rejected."""
    transaction = {
        "transaction_id": "txn_nomerchant",
        "amount": 50.00,
        "currency": "SGD",
        "card_number": "4111111111111111",
        "merchant": ""
    }
    response = client.post("/validate", json=transaction)
    assert response.json()["status"] == "rejected"
    assert "merchant" in response.json()["reason"].lower()