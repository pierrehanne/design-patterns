"""
Chain of Responsibility Pattern
================================
Category: Behavioral Design Pattern

Intent:
    Avoid coupling the sender of a request to its receiver by giving multiple
    objects a chance to handle the request. Chain the receiving objects and pass
    the request along the chain until an object handles it.

When to use:
    - When multiple objects can handle a request and the handler isn't known in advance
    - HTTP middleware pipelines, event processing, support ticket escalation
    - When you want to decouple request senders from receivers
    - When the set of handlers should be configurable dynamically

Key Participants:
    - Handler (interface): Declares method for handling and a reference to the next handler
    - ConcreteHandler: Handles requests it's responsible for, forwards the rest
    - Client: Initiates the request to the first handler in the chain
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


# ---------------------------------------------------------------------------
# Request data
# ---------------------------------------------------------------------------
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SupportTicket:
    id: str
    title: str
    priority: Priority
    description: str
    handled_by: str | None = None


# ---------------------------------------------------------------------------
# Handler interface
# ---------------------------------------------------------------------------
class SupportHandler(ABC):
    """
    Each handler in the chain either handles the ticket or passes it
    to the next handler. This is the core of the pattern.
    """

    def __init__(self) -> None:
        self._next: SupportHandler | None = None

    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        """Chain handlers together. Returns the next handler for fluent chaining."""
        self._next = handler
        return handler

    def handle(self, ticket: SupportTicket) -> SupportTicket:
        """
        Try to handle the ticket. If this handler can't (or shouldn't),
        pass it to the next handler in the chain.
        """
        if self.can_handle(ticket):
            return self.process(ticket)
        elif self._next:
            return self._next.handle(ticket)
        else:
            # End of chain — no one handled it
            print(f"  [Unhandled] Ticket {ticket.id} reached end of chain")
            return ticket

    @abstractmethod
    def can_handle(self, ticket: SupportTicket) -> bool:
        ...

    @abstractmethod
    def process(self, ticket: SupportTicket) -> SupportTicket:
        ...


# ---------------------------------------------------------------------------
# Concrete Handlers — support escalation chain
# ---------------------------------------------------------------------------
class AutoResponder(SupportHandler):
    """Handles LOW priority tickets with automated responses."""

    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.priority == Priority.LOW

    def process(self, ticket: SupportTicket) -> SupportTicket:
        ticket.handled_by = "AutoResponder (Bot)"
        print(f"  [AutoResponder] Ticket {ticket.id}: Sent automated FAQ response")
        return ticket


class Level1Support(SupportHandler):
    """Handles MEDIUM priority tickets — basic troubleshooting."""

    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.priority == Priority.MEDIUM

    def process(self, ticket: SupportTicket) -> SupportTicket:
        ticket.handled_by = "Level 1 Support Agent"
        print(f"  [Level1] Ticket {ticket.id}: Assigned to support agent for troubleshooting")
        return ticket


class Level2Support(SupportHandler):
    """Handles HIGH priority tickets — specialized technical support."""

    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.priority == Priority.HIGH

    def process(self, ticket: SupportTicket) -> SupportTicket:
        ticket.handled_by = "Level 2 Senior Engineer"
        print(f"  [Level2] Ticket {ticket.id}: Escalated to senior engineer")
        return ticket


class ManagerSupport(SupportHandler):
    """Handles CRITICAL tickets — manager intervention required."""

    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.priority == Priority.CRITICAL

    def process(self, ticket: SupportTicket) -> SupportTicket:
        ticket.handled_by = "Support Manager"
        print(f"  [Manager] Ticket {ticket.id}: CRITICAL — Manager notified immediately")
        return ticket


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Build the chain: AutoResponder → Level1 → Level2 → Manager
    auto = AutoResponder()
    l1 = Level1Support()
    l2 = Level2Support()
    manager = ManagerSupport()

    # Chain them together (fluent API)
    auto.set_next(l1)
    l1.set_next(l2)
    l2.set_next(manager)

    # Create test tickets
    tickets = [
        SupportTicket("T-001", "Password reset", Priority.LOW, "Can't remember password"),
        SupportTicket("T-002", "App crashes on login", Priority.MEDIUM, "Error on iOS 17"),
        SupportTicket("T-003", "Data corruption", Priority.HIGH, "User data inconsistent"),
        SupportTicket("T-004", "Full service outage", Priority.CRITICAL, "Production down!"),
    ]

    # Send each ticket through the chain — each finds its appropriate handler
    print("Processing support tickets through the chain:\n")
    for ticket in tickets:
        result = auto.handle(ticket)  # Always start at the first handler
        print(f"    → Handled by: {result.handled_by}\n")
