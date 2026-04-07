"""
State Pattern
=================
Category: Behavioral Design Pattern

Intent:
    Allow an object to alter its behavior when its internal state changes.
    The object will appear to change its class.

When to use:
    - When an object's behavior depends on its state and it must change
      behavior at runtime depending on that state.
    - When you want to eliminate large conditional statements that select
      behavior based on the current state.
    - When transitions between states need to be explicit and controlled.

Key Participants:
    - State (interface): DocumentState -- declares methods that all concrete
      states must implement.
    - ConcreteState: DraftState, ReviewState, PublishedState, ArchivedState --
      each implements behavior appropriate for that state of the context.
    - Context: Document -- maintains a reference to a ConcreteState subclass
      that defines the current state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# State interface
# ---------------------------------------------------------------------------
class DocumentState(ABC):
    """Abstract base class for all document states."""

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def edit(self, doc: Document) -> None: ...

    @abstractmethod
    def submit(self, doc: Document) -> None: ...

    @abstractmethod
    def publish(self, doc: Document) -> None: ...

    @abstractmethod
    def archive(self, doc: Document) -> None: ...


# ---------------------------------------------------------------------------
# Concrete states
# ---------------------------------------------------------------------------
class DraftState(DocumentState):
    """The document is being authored and can be freely edited."""

    def name(self) -> str:
        return "Draft"

    def edit(self, doc: Document) -> None:
        print("  [Draft] Editing document content.")

    def submit(self, doc: Document) -> None:
        print("  [Draft] Submitting document for review.")
        doc.set_state(ReviewState())

    def publish(self, doc: Document) -> None:
        print("  [Draft] ERROR: Cannot publish directly from Draft. Submit for review first.")

    def archive(self, doc: Document) -> None:
        print("  [Draft] Archiving draft document.")
        doc.set_state(ArchivedState())


class ReviewState(DocumentState):
    """The document is under editorial review."""

    def name(self) -> str:
        return "Under Review"

    def edit(self, doc: Document) -> None:
        print("  [Review] Sending document back to Draft for edits.")
        doc.set_state(DraftState())

    def submit(self, doc: Document) -> None:
        print("  [Review] ERROR: Document is already under review.")

    def publish(self, doc: Document) -> None:
        print("  [Review] Review approved. Publishing document.")
        doc.set_state(PublishedState())

    def archive(self, doc: Document) -> None:
        print("  [Review] ERROR: Cannot archive while under review. Publish or reject first.")


class PublishedState(DocumentState):
    """The document is live and visible to readers."""

    def name(self) -> str:
        return "Published"

    def edit(self, doc: Document) -> None:
        print("  [Published] ERROR: Cannot edit a published document. Archive it first.")

    def submit(self, doc: Document) -> None:
        print("  [Published] ERROR: Document is already published.")

    def publish(self, doc: Document) -> None:
        print("  [Published] ERROR: Document is already published.")

    def archive(self, doc: Document) -> None:
        print("  [Published] Archiving published document.")
        doc.set_state(ArchivedState())


class ArchivedState(DocumentState):
    """The document has been archived and is read-only."""

    def name(self) -> str:
        return "Archived"

    def edit(self, doc: Document) -> None:
        print("  [Archived] Un-archiving and moving to Draft for editing.")
        doc.set_state(DraftState())

    def submit(self, doc: Document) -> None:
        print("  [Archived] ERROR: Cannot submit an archived document. Edit it first.")

    def publish(self, doc: Document) -> None:
        print("  [Archived] ERROR: Cannot publish an archived document. Edit it first.")

    def archive(self, doc: Document) -> None:
        print("  [Archived] ERROR: Document is already archived.")


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------
class Document:
    """
    The context object. It delegates state-specific behavior to the current
    state object and allows states to trigger transitions.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self._state: DocumentState = DraftState()

    @property
    def state_name(self) -> str:
        return self._state.name()

    def set_state(self, state: DocumentState) -> None:
        """Transition to a new state (called by state objects)."""
        old = self._state.name()
        self._state = state
        print(f"  >> Document '{self.title}': {old} -> {self._state.name()}")

    def edit(self) -> None:
        print(f"\nDocument '{self.title}' [{self.state_name}]: edit()")
        self._state.edit(self)

    def submit(self) -> None:
        print(f"\nDocument '{self.title}' [{self.state_name}]: submit()")
        self._state.submit(self)

    def publish(self) -> None:
        print(f"\nDocument '{self.title}' [{self.state_name}]: publish()")
        self._state.publish(self)

    def archive(self) -> None:
        print(f"\nDocument '{self.title}' [{self.state_name}]: archive()")
        self._state.archive(self)


# ---------------------------------------------------------------------------
# Runnable example
# ---------------------------------------------------------------------------
def main() -> None:
    doc = Document("Design Patterns Guide")

    # Normal workflow: Draft -> Review -> Published -> Archived
    doc.edit()       # OK: editing in draft
    doc.publish()    # ERROR: can't publish from draft
    doc.submit()     # OK: moves to Review
    doc.publish()    # OK: moves to Published
    doc.edit()       # ERROR: can't edit published doc
    doc.archive()    # OK: moves to Archived

    # Recover from archived: un-archive by editing
    doc.edit()       # OK: moves back to Draft
    doc.submit()     # OK: moves to Review
    doc.edit()       # OK: rejected, back to Draft (for re-editing)
    doc.submit()     # OK: back to Review
    doc.publish()    # OK: Published again


if __name__ == "__main__":
    main()
