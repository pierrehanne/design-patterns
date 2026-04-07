"""
Observer Pattern
=================
Category: Behavioral Design Pattern

Intent:
    Define a one-to-many dependency between objects so that when one object
    changes state, all its dependents are notified and updated automatically.

When to use:
    - When a change to one object requires changing others, and you don't know
      how many objects need to change.
    - When an object should notify other objects without making assumptions
      about who those objects are (loose coupling).
    - When you need a publish-subscribe mechanism.

Key Participants:
    - Subject (Publisher): StockExchange -- maintains a list of observers and
      notifies them of state changes.
    - Observer (Subscriber): PriceDashboard, MobileAlert, TradeLogger --
      objects that want to be notified when the subject's state changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol


# ---------------------------------------------------------------------------
# Observer interface
# ---------------------------------------------------------------------------
class StockObserver(Protocol):
    """Any object that wants to receive stock-price updates."""

    def update(self, symbol: str, price: float) -> None: ...


# ---------------------------------------------------------------------------
# Concrete observers
# ---------------------------------------------------------------------------
class PriceDashboard:
    """Displays the latest prices on a dashboard."""

    def __init__(self, name: str = "Main Dashboard") -> None:
        self.name = name

    def update(self, symbol: str, price: float) -> None:
        print(f"  [{self.name}] {symbol} is now ${price:.2f}")


class MobileAlert:
    """Sends push notifications when a price changes."""

    def __init__(self, threshold: float = 0.0) -> None:
        # Only alert if the price exceeds a threshold (0 = always alert)
        self.threshold = threshold

    def update(self, symbol: str, price: float) -> None:
        if price >= self.threshold or self.threshold == 0.0:
            print(f"  [MobileAlert] PUSH: {symbol} hit ${price:.2f}!")


class TradeLogger:
    """Logs every price change to an audit trail."""

    def __init__(self) -> None:
        self.log: list[str] = []

    def update(self, symbol: str, price: float) -> None:
        entry = f"{symbol}={price:.2f}"
        self.log.append(entry)
        print(f"  [TradeLogger] Logged: {entry}")

    def show_log(self) -> None:
        print(f"  [TradeLogger] Full log: {self.log}")


# ---------------------------------------------------------------------------
# Subject (Publisher)
# ---------------------------------------------------------------------------
@dataclass
class StockExchange:
    """
    The subject that holds current stock prices and notifies observers
    whenever a price is updated.
    """

    _observers: list[StockObserver] = field(default_factory=list, repr=False)
    _prices: dict[str, float] = field(default_factory=dict)

    # -- subscription management --
    def subscribe(self, observer: StockObserver) -> None:
        """Register an observer to receive price updates."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: StockObserver) -> None:
        """Remove an observer so it no longer receives updates."""
        self._observers.remove(observer)

    # -- core logic --
    def set_price(self, symbol: str, price: float) -> None:
        """Update a stock price and notify all observers."""
        self._prices[symbol] = price
        print(f"\nStockExchange: {symbol} updated to ${price:.2f}")
        self._notify(symbol, price)

    def _notify(self, symbol: str, price: float) -> None:
        """Push the update to every registered observer."""
        for observer in self._observers:
            observer.update(symbol, price)


# ---------------------------------------------------------------------------
# Runnable example
# ---------------------------------------------------------------------------
def main() -> None:
    # Create the subject
    exchange = StockExchange()

    # Create observers
    dashboard = PriceDashboard("Trading Floor")
    mobile = MobileAlert(threshold=150.0)
    logger = TradeLogger()

    # Subscribe all three observers
    exchange.subscribe(dashboard)
    exchange.subscribe(mobile)
    exchange.subscribe(logger)

    # Simulate price changes -- all three observers are notified
    exchange.set_price("AAPL", 142.50)
    exchange.set_price("GOOG", 175.30)

    # Unsubscribe the dashboard -- only mobile and logger receive updates
    print("\n--- Dashboard unsubscribed ---")
    exchange.unsubscribe(dashboard)

    exchange.set_price("AAPL", 155.00)  # mobile alert fires (>= 150)

    # Show the full trade log
    print()
    logger.show_log()


if __name__ == "__main__":
    main()
