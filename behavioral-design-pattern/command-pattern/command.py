"""
Command Pattern
===============
Category: Behavioral Design Pattern

Intent:
    Encapsulate a request as an object, thereby letting you parameterize clients
    with different requests, queue or log requests, and support undoable operations.

When to use:
    - When you need undo/redo functionality
    - When you want to queue, schedule, or log operations
    - When you want to decouple the object that invokes an operation from the object that performs it
    - GUI actions, macro recording, transaction systems

Key Participants:
    - Command (interface): Declares execute() and optionally undo()
    - ConcreteCommand: Binds a receiver to an action
    - Receiver: Knows how to perform the actual work
    - Invoker: Asks the command to carry out the request
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Receiver — the text document that commands operate on
# ---------------------------------------------------------------------------
class TextDocument:
    def __init__(self) -> None:
        self.content: str = ""

    def insert(self, position: int, text: str) -> None:
        self.content = self.content[:position] + text + self.content[position:]

    def delete(self, position: int, length: int) -> str:
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted

    def __str__(self) -> str:
        return f'"{self.content}"'


# ---------------------------------------------------------------------------
# Command interface
# ---------------------------------------------------------------------------
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...

    @abstractmethod
    def description(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Concrete Commands — each encapsulates one operation + its undo
# ---------------------------------------------------------------------------
class InsertCommand(Command):
    """Inserts text at a position. Undo removes it."""

    def __init__(self, document: TextDocument, position: int, text: str) -> None:
        self._doc = document
        self._position = position
        self._text = text

    def execute(self) -> None:
        self._doc.insert(self._position, self._text)

    def undo(self) -> None:
        self._doc.delete(self._position, len(self._text))

    def description(self) -> str:
        return f'Insert "{self._text}" at position {self._position}'


class DeleteCommand(Command):
    """Deletes text at a position. Undo re-inserts it."""

    def __init__(self, document: TextDocument, position: int, length: int) -> None:
        self._doc = document
        self._position = position
        self._length = length
        self._deleted_text: str = ""  # Saved on execute for undo

    def execute(self) -> None:
        self._deleted_text = self._doc.delete(self._position, self._length)

    def undo(self) -> None:
        self._doc.insert(self._position, self._deleted_text)

    def description(self) -> str:
        return f'Delete {self._length} chars at position {self._position}'


class ReplaceCommand(Command):
    """Replaces text. Composed of delete + insert for undo support."""

    def __init__(self, document: TextDocument, position: int, length: int, new_text: str) -> None:
        self._doc = document
        self._position = position
        self._length = length
        self._new_text = new_text
        self._old_text: str = ""

    def execute(self) -> None:
        self._old_text = self._doc.delete(self._position, self._length)
        self._doc.insert(self._position, self._new_text)

    def undo(self) -> None:
        self._doc.delete(self._position, len(self._new_text))
        self._doc.insert(self._position, self._old_text)

    def description(self) -> str:
        return f'Replace {self._length} chars at position {self._position} with "{self._new_text}"'


# ---------------------------------------------------------------------------
# Invoker — manages command history for undo/redo
# ---------------------------------------------------------------------------
class TextEditor:
    """
    The invoker. Executes commands and maintains history stacks
    for undo and redo operations.
    """

    def __init__(self, document: TextDocument) -> None:
        self.document = document
        self._history: list[Command] = []      # Undo stack
        self._redo_stack: list[Command] = []    # Redo stack

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()  # New action invalidates redo history
        print(f"  [Execute] {command.description()} → {self.document}")

    def undo(self) -> None:
        if not self._history:
            print("  [Undo] Nothing to undo")
            return
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        print(f"  [Undo] {command.description()} → {self.document}")

    def redo(self) -> None:
        if not self._redo_stack:
            print("  [Redo] Nothing to redo")
            return
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        print(f"  [Redo] {command.description()} → {self.document}")


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    doc = TextDocument()
    editor = TextEditor(doc)

    print("=== Building a document ===")
    editor.execute(InsertCommand(doc, 0, "Hello World"))
    editor.execute(InsertCommand(doc, 5, ","))
    editor.execute(InsertCommand(doc, len(doc.content), "!"))
    editor.execute(ReplaceCommand(doc, 7, 5, "Python"))

    print("\n=== Undo operations ===")
    editor.undo()  # Undo replace
    editor.undo()  # Undo "!"
    editor.undo()  # Undo ","

    print("\n=== Redo operations ===")
    editor.redo()  # Redo ","
    editor.redo()  # Redo "!"

    print("\n=== Delete and undo ===")
    editor.execute(DeleteCommand(doc, 0, 5))  # Delete "Hello"
    editor.undo()  # Bring "Hello" back
