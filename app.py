"""
FinSecure Pay — Transaction Validation API
A simple FastAPI service that validates financial transactions.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="FinSecure Pay Transaction Validator",
    description="API for validating payment transactions",
    version="1.0.0"
)


# Input model: what a transaction looks like
class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code (e.g., USD, SGD)")
    card_number: str = Field(..., description="Card number")
    merchant: str = Field(..., description="Merchant name")


# Output model: what the response looks like
class ValidationResult(BaseModel):
    transaction_id: str
    status: str  # "approved" or "rejected"
    reason: str


# -------- ENDPOINTS --------

@app.get("/health")
def health_check():
    """Health check endpoint — returns the service status."""
    return {"status": "healthy", "service": "finsecure-pay"}


@app.post("/validate", response_model=ValidationResult)
def validate_transaction(transaction: Transaction):
    """
    Validate a transaction against business rules.
    Returns 'approved' or 'rejected' with a reason.
    """

    # Rule 1: Amount must be positive
    if transaction.amount <= 0:
        return ValidationResult(
            transaction_id=transaction.transaction_id,
            status="rejected",
            reason="Transaction amount must be greater than zero"
        )

    # Rule 2: Amount must not exceed $10,000
    if transaction.amount > 10000:
        return ValidationResult(
            transaction_id=transaction.transaction_id,
            status="rejected",
            reason="Transaction amount exceeds maximum limit of 10,000"
        )

    # Rule 3: Currency must be supported
    supported_currencies = ["USD", "SGD", "EUR", "GBP"]
    if transaction.currency.upper() not in supported_currencies:
        return ValidationResult(
            transaction_id=transaction.transaction_id,
            status="rejected",
            reason=f"Currency {transaction.currency} not supported"
        )

    # Rule 4: Card number must be at least 13 digits
    cleaned_card = transaction.card_number.replace(" ", "").replace("-", "")
    if not cleaned_card.isdigit() or len(cleaned_card) < 13 or len(cleaned_card) > 19:
        return ValidationResult(
            transaction_id=transaction.transaction_id,
            status="rejected",
            reason="Invalid card number format"
        )

    # Rule 5: Merchant name is required
    if not transaction.merchant or len(transaction.merchant.strip()) == 0:
        return ValidationResult(
            transaction_id=transaction.transaction_id,
            status="rejected",
            reason="Merchant name is required"
        )

    # All rules passed — approve
    return ValidationResult(
        transaction_id=transaction.transaction_id,
        status="approved",
        reason="Transaction passed all validation checks"
    )