"""
Strategy Pattern
=================
Category: Behavioral Design Pattern

Intent:
    Define a family of algorithms, encapsulate each one, and make them
    interchangeable. Strategy lets the algorithm vary independently from
    the clients that use it.

When to use:
    - When you have multiple algorithms for a specific task and want to
      switch between them at runtime.
    - When you want to avoid conditional statements for selecting behaviors.
    - When a class has many related behaviors that differ only in their
      implementation.

Key Participants:
    - Strategy (interface): PaymentStrategy -- declares the interface common
      to all supported algorithms.
    - ConcreteStrategy: CreditCardPayment, PayPalPayment, CryptoPayment --
      implements the algorithm using the Strategy interface.
    - Context: PaymentContext -- maintains a reference to a Strategy object
      and delegates the work to it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Strategy interface
# ---------------------------------------------------------------------------
class PaymentStrategy(ABC):
    """Abstract base for all payment strategies."""

    @abstractmethod
    def pay(self, amount: float) -> str:
        """Process a payment and return a confirmation message."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the payment method."""
        ...


# ---------------------------------------------------------------------------
# Concrete strategies
# ---------------------------------------------------------------------------
@dataclass
class CreditCardPayment(PaymentStrategy):
    """Processes payments via credit card."""

    card_number: str
    cardholder: str

    def pay(self, amount: float) -> str:
        masked = f"****-****-****-{self.card_number[-4:]}"
        return (
            f"Charged ${amount:.2f} to credit card {masked} "
            f"(holder: {self.cardholder})"
        )

    def name(self) -> str:
        return "Credit Card"


@dataclass
class PayPalPayment(PaymentStrategy):
    """Processes payments via PayPal."""

    email: str

    def pay(self, amount: float) -> str:
        return f"Sent ${amount:.2f} via PayPal to {self.email}"

    def name(self) -> str:
        return "PayPal"


@dataclass
class CryptoPayment(PaymentStrategy):
    """Processes payments via cryptocurrency."""

    wallet_address: str
    currency: str = "BTC"

    def pay(self, amount: float) -> str:
        short_addr = f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"
        return (
            f"Transferred ${amount:.2f} in {self.currency} "
            f"to wallet {short_addr}"
        )

    def name(self) -> str:
        return f"Crypto ({self.currency})"


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------
class PaymentContext:
    """
    The context that clients interact with. It delegates the actual payment
    processing to whatever strategy is currently set.
    """

    def __init__(self, strategy: PaymentStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> PaymentStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PaymentStrategy) -> None:
        """Swap the payment strategy at runtime."""
        self._strategy = strategy

    def checkout(self, amount: float) -> None:
        """Process a payment using the current strategy."""
        print(f"Processing ${amount:.2f} via {self._strategy.name()}...")
        result = self._strategy.pay(amount)
        print(f"  -> {result}\n")


# ---------------------------------------------------------------------------
# Runnable example
# ---------------------------------------------------------------------------
def main() -> None:
    # Start with credit card
    cc = CreditCardPayment(card_number="4111111111111234", cardholder="Alice")
    ctx = PaymentContext(cc)
    ctx.checkout(99.99)

    # Swap to PayPal at runtime
    paypal = PayPalPayment(email="alice@example.com")
    ctx.strategy = paypal
    ctx.checkout(49.50)

    # Swap to crypto at runtime
    crypto = CryptoPayment(
        wallet_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        currency="ETH",
    )
    ctx.strategy = crypto
    ctx.checkout(250.00)

    # Demonstrate that the context is agnostic to the concrete strategy
    strategies: list[PaymentStrategy] = [cc, paypal, crypto]
    print("--- Batch processing with all strategies ---")
    for strat in strategies:
        ctx.strategy = strat
        ctx.checkout(10.00)


if __name__ == "__main__":
    main()
