"""
Adapter Pattern
===============
Category: Structural Design Pattern

Intent:
    Convert the interface of a class into another interface that clients expect.
    Adapter lets classes work together that couldn't otherwise because of
    incompatible interfaces. It acts as a translator between old and new code.

When to use:
    - When you want to use an existing class but its interface doesn't match yours
    - When integrating third-party libraries or legacy systems
    - When migrating from one API to another without rewriting client code

Key Participants:
    - Target: The interface the client expects
    - Adaptee: The existing class with an incompatible interface
    - Adapter: Translates calls from Target interface to Adaptee interface
    - Client: Works with the Target interface, unaware of the Adapter
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Target — the modern payment interface our system uses
# ---------------------------------------------------------------------------
class PaymentProcessor(ABC):
    """The interface our checkout system expects."""

    @abstractmethod
    def charge(self, amount_cents: int, currency: str, card_token: str) -> dict:
        """Charge a card and return a standardized result."""
        ...

    @abstractmethod
    def refund(self, transaction_id: str, amount_cents: int) -> dict:
        ...


# ---------------------------------------------------------------------------
# Adaptee — a legacy payment gateway with a completely different API
# ---------------------------------------------------------------------------
class LegacyPaymentGateway:
    """
    An old payment system we can't modify. Uses dollars (not cents),
    different method names, and returns XML-like strings instead of dicts.
    """

    def make_payment(self, dollars: float, card_number: str, curr: str) -> str:
        # Simulates an old API that returns a pipe-delimited string
        return f"OK|TXN-{id(self)}|{dollars}|{curr}"

    def reverse_payment(self, txn_ref: str) -> str:
        return f"REVERSED|{txn_ref}"


# ---------------------------------------------------------------------------
# Adapter — bridges the gap between Target and Adaptee
# ---------------------------------------------------------------------------
class LegacyPaymentAdapter(PaymentProcessor):
    """
    Wraps the LegacyPaymentGateway and translates its interface to match
    the modern PaymentProcessor interface. This is the core of the pattern:
    the client calls `charge()` and the adapter calls `make_payment()` internally.
    """

    def __init__(self, legacy_gateway: LegacyPaymentGateway) -> None:
        self._gateway = legacy_gateway

    def charge(self, amount_cents: int, currency: str, card_token: str) -> dict:
        # Translate: our system uses cents, legacy uses dollars
        dollars = amount_cents / 100.0

        # Translate: our system uses tokens, legacy expects card numbers
        # (In reality, the adapter might call a token-to-card lookup service)
        card_number = f"****-****-****-{card_token[-4:]}"

        # Call the legacy API
        result = self._gateway.make_payment(dollars, card_number, currency)

        # Translate the response from legacy format to our standardized format
        parts = result.split("|")
        return {
            "success": parts[0] == "OK",
            "transaction_id": parts[1],
            "amount_cents": amount_cents,
            "currency": currency,
        }

    def refund(self, transaction_id: str, amount_cents: int) -> dict:
        result = self._gateway.reverse_payment(transaction_id)
        parts = result.split("|")
        return {
            "success": parts[0] == "REVERSED",
            "transaction_id": transaction_id,
            "refunded_cents": amount_cents,
        }


# ---------------------------------------------------------------------------
# A modern payment processor (no adapter needed)
# ---------------------------------------------------------------------------
class StripeProcessor(PaymentProcessor):
    """A modern processor that already conforms to our interface."""

    def charge(self, amount_cents: int, currency: str, card_token: str) -> dict:
        return {
            "success": True,
            "transaction_id": f"stripe-{id(self)}",
            "amount_cents": amount_cents,
            "currency": currency,
        }

    def refund(self, transaction_id: str, amount_cents: int) -> dict:
        return {
            "success": True,
            "transaction_id": transaction_id,
            "refunded_cents": amount_cents,
        }


# ---------------------------------------------------------------------------
# Client Code — works with any PaymentProcessor, doesn't know about adapters
# ---------------------------------------------------------------------------
def process_checkout(processor: PaymentProcessor, amount_cents: int) -> None:
    """This function has no idea if it's talking to Stripe or a wrapped legacy system."""
    result = processor.charge(amount_cents, "USD", "tok_visa_4242")
    if result["success"]:
        print(f"  Charged {amount_cents} cents — txn: {result['transaction_id']}")
    else:
        print("  Payment failed!")


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Modern processor — works directly
    print("Using modern Stripe processor:")
    stripe = StripeProcessor()
    process_checkout(stripe, 2999)

    # Legacy system — wrap it with an adapter
    print("\nUsing adapted legacy gateway:")
    legacy = LegacyPaymentGateway()
    adapted = LegacyPaymentAdapter(legacy)
    process_checkout(adapted, 2999)

    # Both are interchangeable through the same interface
    print("\nRefund through adapted legacy:")
    refund_result = adapted.refund("TXN-12345", 2999)
    print(f"  Refund result: {refund_result}")
