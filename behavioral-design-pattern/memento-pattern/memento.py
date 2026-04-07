"""
Memento Pattern
================
Category: Behavioral Design Pattern

Intent:
    Without violating encapsulation, capture and externalize an object's
    internal state so that the object can be restored to this state later.

When to use:
    - You need to save and restore snapshots of an object's state
    - A direct interface to obtaining the state would expose implementation
      details and break encapsulation
    - You need undo/rollback functionality

Key Participants:
    - Originator (GameCharacter): the object whose state needs saving;
      creates a memento containing a snapshot of its current internal state
    - Memento (GameSave): stores the originator's internal state;
      protects against access by objects other than the originator
    - Caretaker (SaveManager): responsible for keeping the memento safe;
      never operates on or examines the contents of a memento
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


# --- Memento ---

@dataclass(frozen=True)
class GameSave:
    """
    Memento: an immutable snapshot of the character's state.
    frozen=True prevents anyone from tampering with the saved state.
    """
    health: int
    level: int
    position_x: float
    position_y: float
    inventory: tuple[str, ...]  # immutable copy of inventory
    timestamp: str
    label: str

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] '{self.label}' -- "
            f"HP:{self.health} Lv:{self.level} "
            f"Pos:({self.position_x},{self.position_y}) "
            f"Items:{list(self.inventory)}"
        )


# --- Originator ---

class GameCharacter:
    """
    Originator: the game character whose state we want to save and restore.
    Only the character itself knows how to create and restore from a memento.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.health = 100
        self.level = 1
        self.position_x = 0.0
        self.position_y = 0.0
        self.inventory: list[str] = []

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)
        print(f"  {self.name} took {amount} damage. HP: {self.health}")

    def level_up(self) -> None:
        self.level += 1
        self.health = 100  # full heal on level up
        print(f"  {self.name} leveled up to Lv.{self.level}! HP restored.")

    def move_to(self, x: float, y: float) -> None:
        self.position_x = x
        self.position_y = y
        print(f"  {self.name} moved to ({x}, {y})")

    def pick_up(self, item: str) -> None:
        self.inventory.append(item)
        print(f"  {self.name} picked up '{item}'")

    # --- Memento creation and restoration ---

    def save(self, label: str) -> GameSave:
        """Create a memento capturing the current state."""
        memento = GameSave(
            health=self.health,
            level=self.level,
            position_x=self.position_x,
            position_y=self.position_y,
            inventory=tuple(self.inventory),  # snapshot as immutable tuple
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            label=label,
        )
        print(f"  >> State saved: '{label}'")
        return memento

    def restore(self, memento: GameSave) -> None:
        """Restore state from a memento."""
        self.health = memento.health
        self.level = memento.level
        self.position_x = memento.position_x
        self.position_y = memento.position_y
        self.inventory = list(memento.inventory)  # mutable copy from tuple
        print(f"  >> State restored from '{memento.label}'")

    def status(self) -> str:
        return (
            f"  {self.name}: HP={self.health} Lv={self.level} "
            f"Pos=({self.position_x},{self.position_y}) "
            f"Inventory={self.inventory}"
        )


# --- Caretaker ---

class SaveManager:
    """
    Caretaker: manages a collection of saves without knowing their internals.
    It never inspects or modifies the memento's state.
    """

    def __init__(self) -> None:
        self._saves: dict[str, GameSave] = {}

    def store(self, key: str, save: GameSave) -> None:
        """Store a save under a named slot."""
        self._saves[key] = save

    def load(self, key: str) -> GameSave | None:
        """Retrieve a save by slot name."""
        save = self._saves.get(key)
        if save is None:
            print(f"  >> No save found for slot '{key}'")
        return save

    def list_saves(self) -> None:
        """List all stored saves."""
        if not self._saves:
            print("  No saves stored.")
            return
        print("  Stored saves:")
        for key, save in self._saves.items():
            print(f"    [{key}] {save}")


# --- Main ---

def main() -> None:
    hero = GameCharacter("Warrior")
    manager = SaveManager()

    print("=== Starting the adventure ===")
    print(hero.status())
    print()

    # Play through some actions
    hero.move_to(10.0, 20.0)
    hero.pick_up("Iron Sword")
    hero.level_up()
    print(hero.status())
    print()

    # Save at checkpoint 1
    checkpoint1 = hero.save("Before the dungeon")
    manager.store("checkpoint1", checkpoint1)
    print()

    # Enter the dungeon -- things go badly
    hero.move_to(50.0, 80.0)
    hero.take_damage(60)
    hero.pick_up("Rusty Key")
    hero.take_damage(30)
    print(hero.status())
    print()

    # Save the risky state too
    checkpoint2 = hero.save("Deep in dungeon (low HP)")
    manager.store("checkpoint2", checkpoint2)
    print()

    # Even worse...
    hero.take_damage(50)
    print(hero.status())
    print()

    # List all saves
    print("=== Reviewing saves ===")
    manager.list_saves()
    print()

    # Restore to the safe checkpoint
    print("=== Restoring to checkpoint 1 ===")
    save = manager.load("checkpoint1")
    if save:
        hero.restore(save)
    print(hero.status())


if __name__ == "__main__":
    main()
