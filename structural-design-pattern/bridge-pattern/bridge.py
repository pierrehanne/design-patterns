"""
Bridge Pattern
==============
Category: Structural Design Pattern

Intent:
    Decouple an abstraction from its implementation so the two can vary
    independently. Instead of one large class hierarchy, split it into two
    separate hierarchies — abstraction and implementation — connected by
    composition (the "bridge").

When to use:
    - When you'd otherwise need a combinatorial explosion of subclasses
      (e.g., 3 notification types x 4 delivery channels = 12 classes without bridge)
    - When both the abstraction and implementation need to be extensible
    - When you want to switch implementations at runtime

Key Participants:
    - Abstraction: High-level interface (e.g., notification urgency)
    - Implementation: Low-level interface (e.g., delivery channel)
    - The "bridge" is the reference from Abstraction to Implementation

Difference from Adapter:
    - Adapter makes two EXISTING incompatible interfaces work together
    - Bridge is designed UP FRONT to let abstraction and implementation vary independently
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ---------------------------------------------------------------------------
# Implementation hierarchy — delivery channels
# ---------------------------------------------------------------------------
class MessageChannel(ABC):
    """The implementation interface. Each channel knows HOW to deliver a message."""

    @abstractmethod
    def send(self, title: str, body: str, recipient: str) -> str:
        ...


class EmailChannel(MessageChannel):
    def send(self, title: str, body: str, recipient: str) -> str:
        return f"[Email → {recipient}] Subject: {title} | {body}"


class SMSChannel(MessageChannel):
    def send(self, title: str, body: str, recipient: str) -> str:
        # SMS has character limits, so we truncate
        short = body[:160] if len(body) > 160 else body
        return f"[SMS → {recipient}] {short}"


class SlackChannel(MessageChannel):
    def __init__(self, workspace: str = "default") -> None:
        self.workspace = workspace

    def send(self, title: str, body: str, recipient: str) -> str:
        return f"[Slack#{self.workspace} → @{recipient}] *{title}*\n{body}"


# ---------------------------------------------------------------------------
# Abstraction hierarchy — notification types (urgency levels)
# ---------------------------------------------------------------------------
class Notification(ABC):
    """
    The abstraction. Holds a reference to a MessageChannel (the bridge).
    Subclasses define WHAT to send; the channel defines HOW to deliver it.
    """

    def __init__(self, channel: MessageChannel) -> None:
        # This is the "bridge" — composition, not inheritance
        self._channel = channel

    @abstractmethod
    def notify(self, recipient: str, message: str) -> str:
        ...


class RegularNotification(Notification):
    """Standard priority — sends as-is."""

    def notify(self, recipient: str, message: str) -> str:
        return self._channel.send("Notification", message, recipient)


class UrgentNotification(Notification):
    """High priority — adds urgency markers and timestamp."""

    def notify(self, recipient: str, message: str) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        title = "URGENT"
        body = f"[{timestamp}] {message} — Immediate action required!"
        return self._channel.send(title, body, recipient)


class ScheduledNotification(Notification):
    """Deferred — includes scheduled delivery time."""

    def __init__(self, channel: MessageChannel, scheduled_time: str) -> None:
        super().__init__(channel)
        self.scheduled_time = scheduled_time

    def notify(self, recipient: str, message: str) -> str:
        title = f"Scheduled ({self.scheduled_time})"
        body = f"{message} [Will be delivered at {self.scheduled_time}]"
        return self._channel.send(title, body, recipient)


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Without Bridge: 3 notification types × 3 channels = 9 classes
    # With Bridge:    3 notification types + 3 channels  = 6 classes

    # Mix and match any notification type with any channel
    print("=== Regular via Email ===")
    print(RegularNotification(EmailChannel()).notify("alice@co.com", "Your report is ready"))

    print("\n=== Urgent via SMS ===")
    print(UrgentNotification(SMSChannel()).notify("555-1234", "Server CPU at 98%"))

    print("\n=== Urgent via Slack ===")
    print(UrgentNotification(SlackChannel("ops")).notify("oncall", "Database failover triggered"))

    print("\n=== Scheduled via Email ===")
    scheduled = ScheduledNotification(EmailChannel(), "2025-03-15 09:00")
    print(scheduled.notify("team@co.com", "Weekly standup reminder"))

    # Swap channel at runtime
    print("\n=== Same notification, different channel ===")
    for channel in [EmailChannel(), SMSChannel(), SlackChannel("general")]:
        notif = UrgentNotification(channel)
        print(notif.notify("bob", "Deploy failed"))
