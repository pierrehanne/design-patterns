"""
Mediator Pattern
=================
Category: Behavioral Design Pattern

Intent:
    Define an object that encapsulates how a set of objects interact.
    The Mediator promotes loose coupling by keeping objects from referring
    to each other explicitly, and lets you vary their interaction independently.

When to use:
    - A set of objects communicate in well-defined but complex ways
    - Reusing an object is difficult because it refers to many other objects
    - Behavior distributed between several classes should be customizable
      without a lot of subclassing

Key Participants:
    - Mediator: defines the interface for communication between Colleague objects
    - ConcreteMediator (ChatRoom): coordinates communication between Colleague objects
    - Colleague (User): each Colleague communicates with its Mediator whenever
      it would have otherwise communicated with another Colleague
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime


# --- Mediator Interface ---

class ChatMediator(ABC):
    """Abstract mediator that defines the communication contract."""

    @abstractmethod
    def send_message(self, message: str, sender: User, recipient: User | None = None) -> None:
        """Send a message. If recipient is None, broadcast to all."""
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        """Register a user with the mediator."""
        pass


# --- Colleague ---

class User:
    """A chat participant that communicates through the mediator, never directly."""

    def __init__(self, name: str, mediator: ChatMediator) -> None:
        self.name = name
        self.mediator = mediator
        self.inbox: list[str] = []
        # Automatically register with the mediator upon creation
        self.mediator.add_user(self)

    def send(self, message: str, recipient: User | None = None) -> None:
        """Send a message through the mediator (broadcast or direct)."""
        target = f" to {recipient.name}" if recipient else " to everyone"
        print(f"[{self.name}] sends '{message}'{target}")
        self.mediator.send_message(message, sender=self, recipient=recipient)

    def receive(self, message: str, sender: User) -> None:
        """Called by the mediator when a message is delivered to this user."""
        formatted = f"  [{self.name}] received from {sender.name}: '{message}'"
        print(formatted)
        self.inbox.append(f"{sender.name}: {message}")


# --- Concrete Mediator ---

class ChatRoom(ChatMediator):
    """
    Concrete mediator that manages users and routes messages.
    Users never talk directly to each other -- they always go through the room.
    """

    def __init__(self, room_name: str) -> None:
        self.room_name = room_name
        self._users: list[User] = []
        self._log: list[str] = []

    def add_user(self, user: User) -> None:
        self._users.append(user)
        print(f"  >> {user.name} joined '{self.room_name}'")

    def send_message(self, message: str, sender: User, recipient: User | None = None) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")

        if recipient is not None:
            # Direct message -- only deliver to the specified recipient
            if recipient not in self._users:
                print(f"  >> Error: {recipient.name} is not in the room")
                return
            recipient.receive(message, sender)
            self._log.append(f"[{timestamp}] DM {sender.name} -> {recipient.name}: {message}")
        else:
            # Broadcast -- deliver to every user except the sender
            for user in self._users:
                if user is not sender:
                    user.receive(message, sender)
            self._log.append(f"[{timestamp}] BROADCAST {sender.name}: {message}")

    def show_log(self) -> None:
        """Display the full message history kept by the mediator."""
        print(f"\n--- Chat log for '{self.room_name}' ---")
        for entry in self._log:
            print(f"  {entry}")


# --- Main ---

def main() -> None:
    # Create the mediator (chat room)
    room = ChatRoom("Design Patterns Study Group")

    # Create colleagues (users) -- they register themselves with the room
    alice = User("Alice", room)
    bob = User("Bob", room)
    charlie = User("Charlie", room)

    print()

    # Broadcast: Alice sends a message to everyone in the room
    alice.send("Hey everyone, ready to discuss the Mediator pattern?")
    print()

    # Direct message: Bob replies only to Alice
    bob.send("Sure, I just finished reading about it!", recipient=alice)
    print()

    # Broadcast: Charlie shares with the group
    charlie.send("The key insight is that colleagues don't know about each other.")
    print()

    # Direct message: Alice to Charlie
    alice.send("Exactly! The mediator handles all the routing.", recipient=charlie)

    # Show the centralized log maintained by the mediator
    room.show_log()

    # Demonstrate that each user keeps its own inbox
    print(f"\nAlice's inbox: {alice.inbox}")
    print(f"Bob's inbox:   {bob.inbox}")


if __name__ == "__main__":
    main()
