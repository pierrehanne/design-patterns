"""
Factory Method Pattern
======================
Category: Creational Design Pattern

Intent:
    Define an interface for creating objects, but let subclasses (or a factory
    function) decide which concrete class to instantiate. The client code works
    with the product interface and never needs to know the concrete type.

When to use:
    - When a class can't anticipate the type of objects it needs to create
    - When you want to centralize and encapsulate object creation logic
    - When adding new product types should NOT require changing existing code

Key Participants:
    - Product (interface): Defines the interface all concrete products implement
    - ConcreteProduct: Specific implementations (EmailNotification, SMSNotification, etc.)
    - Creator / Factory: Contains the factory method that returns Product instances
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Product Interface
# ---------------------------------------------------------------------------
class Notification(ABC):
    """Abstract product — all notifications must implement `send`."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> str:
        ...


# ---------------------------------------------------------------------------
# Concrete Products
# ---------------------------------------------------------------------------
@dataclass
class EmailNotification(Notification):
    sender: str = "noreply@example.com"

    def send(self, recipient: str, message: str) -> str:
        return f"[Email] From {self.sender} to {recipient}: {message}"


@dataclass
class SMSNotification(Notification):
    phone_prefix: str = "+1"

    def send(self, recipient: str, message: str) -> str:
        return f"[SMS] To {self.phone_prefix}{recipient}: {message}"


@dataclass
class PushNotification(Notification):
    platform: str = "mobile"

    def send(self, recipient: str, message: str) -> str:
        return f"[Push/{self.platform}] To {recipient}: {message}"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
class NotificationFactory:
    """
    Factory that creates the correct Notification subclass based on a string key.
    New notification types can be registered without modifying existing code.
    """

    # Registry maps type names to their constructors
    _registry: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }

    @classmethod
    def create(cls, channel: str, **kwargs) -> Notification:
        """Create a notification by channel name. Raises ValueError for unknown types."""
        klass = cls._registry.get(channel)
        if klass is None:
            available = ", ".join(cls._registry.keys())
            raise ValueError(f"Unknown channel '{channel}'. Available: {available}")
        return klass(**kwargs)

    @classmethod
    def register(cls, channel: str, klass: type[Notification]) -> None:
        """Register a new notification type at runtime — open/closed principle."""
        cls._registry[channel] = klass


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Client code only depends on Notification interface, not concrete classes
    factory = NotificationFactory()

    for channel in ("email", "sms", "push"):
        notification = factory.create(channel)
        print(notification.send("user@example.com", "Your order has shipped!"))

    # Demonstrate extensibility: add a new type without modifying the factory
    @dataclass
    class SlackNotification(Notification):
        workspace: str = "general"

        def send(self, recipient: str, message: str) -> str:
            return f"[Slack#{self.workspace}] @{recipient}: {message}"

    factory.register("slack", SlackNotification)
    slack = factory.create("slack", workspace="engineering")
    print(slack.send("alice", "Deploy complete!"))
