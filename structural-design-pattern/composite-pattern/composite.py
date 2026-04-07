"""
Composite Pattern
=================
Category: Structural Design Pattern

Intent:
    Compose objects into tree structures to represent part-whole hierarchies.
    Lets clients treat individual objects (leaves) and compositions (branches)
    uniformly through a common interface.

When to use:
    - When you have a tree/hierarchical structure (files/folders, org charts, UI components)
    - When clients should treat single objects and groups the same way
    - When operations should propagate recursively through the tree

Key Participants:
    - Component: Common interface for both leaves and composites
    - Leaf: End node with no children (e.g., a File)
    - Composite: Node that contains children (e.g., a Directory)
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Component — common interface
# ---------------------------------------------------------------------------
class FileSystemEntry(ABC):
    """Every entry in the file system — file or directory — shares this interface."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def size(self) -> int:
        """Returns the size in bytes."""
        ...

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        """Returns a tree-like string representation."""
        ...

    @abstractmethod
    def search(self, keyword: str) -> list[str]:
        """Find entries whose name contains the keyword."""
        ...


# ---------------------------------------------------------------------------
# Leaf — a file (no children)
# ---------------------------------------------------------------------------
class File(FileSystemEntry):
    def __init__(self, name: str, size_bytes: int) -> None:
        super().__init__(name)
        self._size = size_bytes

    def size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}📄 {self.name} ({self._size} bytes)"

    def search(self, keyword: str) -> list[str]:
        if keyword.lower() in self.name.lower():
            return [self.name]
        return []


# ---------------------------------------------------------------------------
# Composite — a directory (has children)
# ---------------------------------------------------------------------------
class Directory(FileSystemEntry):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._children: list[FileSystemEntry] = []

    def add(self, entry: FileSystemEntry) -> "Directory":
        """Add a child (file or subdirectory). Returns self for chaining."""
        self._children.append(entry)
        return self

    def remove(self, name: str) -> None:
        self._children = [c for c in self._children if c.name != name]

    def size(self) -> int:
        # Recursively sums sizes of all children — uniform treatment
        return sum(child.size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}📁 {self.name}/ ({self.size()} bytes)"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

    def search(self, keyword: str) -> list[str]:
        results: list[str] = []
        if keyword.lower() in self.name.lower():
            results.append(self.name + "/")
        for child in self._children:
            results.extend(child.search(keyword))
        return results


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Build a file system tree
    root = Directory("project")

    src = Directory("src")
    src.add(File("main.py", 2048))
    src.add(File("utils.py", 1024))
    src.add(File("config.py", 512))

    tests = Directory("tests")
    tests.add(File("test_main.py", 1536))
    tests.add(File("test_utils.py", 768))

    docs = Directory("docs")
    docs.add(File("README.md", 4096))
    docs.add(File("CHANGELOG.md", 2048))

    root.add(src)
    root.add(tests)
    root.add(docs)
    root.add(File(".gitignore", 128))

    # Display the tree — works uniformly for files and directories
    print(root.display())

    # Size calculation propagates through the tree
    print(f"\nTotal project size: {root.size()} bytes")
    print(f"Source code size: {src.size()} bytes")

    # Search works recursively across the entire tree
    print(f"\nSearch for 'test': {root.search('test')}")
    print(f"Search for 'main': {root.search('main')}")
