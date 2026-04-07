"""
Decorator Pattern
=================
Category: Structural Design Pattern

Intent:
    Attach additional responsibilities to an object dynamically. Decorators
    provide a flexible alternative to subclassing for extending functionality.
    Each decorator wraps the original and adds one behavior.

When to use:
    - When you want to add behavior to objects without modifying their class
    - When extension by subclassing leads to a combinatorial explosion
    - When behaviors need to be combined in arbitrary ways at runtime
    - Follows the Open/Closed Principle: open for extension, closed for modification

Key Participants:
    - Component (interface): The base interface
    - ConcreteComponent: The original object being decorated
    - Decorator (base): Wraps a Component and delegates to it
    - ConcreteDecorator: Adds specific behavior before/after delegating
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Component — the base interface for data streams
# ---------------------------------------------------------------------------
class DataSource(ABC):
    """Interface for reading/writing data."""

    @abstractmethod
    def write(self, data: str) -> str:
        """Process data for writing and return the processed result."""
        ...

    @abstractmethod
    def read(self, data: str) -> str:
        """Process data for reading (reverse of write) and return the result."""
        ...


# ---------------------------------------------------------------------------
# Concrete Component — the base implementation
# ---------------------------------------------------------------------------
class StringDataSource(DataSource):
    """Stores data as a plain string. No processing."""

    def write(self, data: str) -> str:
        return data  # Store as-is

    def read(self, data: str) -> str:
        return data  # Return as-is


# ---------------------------------------------------------------------------
# Base Decorator — wraps a DataSource and delegates to it
# ---------------------------------------------------------------------------
class DataSourceDecorator(DataSource, ABC):
    """
    Base decorator. Holds a reference to the wrapped component.
    Subclasses override write/read to add behavior, then delegate to the wrapper.
    """

    def __init__(self, wrapped: DataSource) -> None:
        self._wrapped = wrapped

    def write(self, data: str) -> str:
        return self._wrapped.write(data)

    def read(self, data: str) -> str:
        return self._wrapped.read(data)


# ---------------------------------------------------------------------------
# Concrete Decorators — each adds one specific behavior
# ---------------------------------------------------------------------------
class EncryptionDecorator(DataSourceDecorator):
    """Adds simple encryption (Caesar cipher for demo purposes)."""

    def __init__(self, wrapped: DataSource, shift: int = 3) -> None:
        super().__init__(wrapped)
        self._shift = shift

    def write(self, data: str) -> str:
        # Encrypt before passing to the next layer
        encrypted = "".join(
            chr((ord(c) - 32 + self._shift) % 95 + 32) if 32 <= ord(c) < 127 else c
            for c in data
        )
        return self._wrapped.write(encrypted)

    def read(self, data: str) -> str:
        # First let the inner layer process, then decrypt
        inner = self._wrapped.read(data)
        return "".join(
            chr((ord(c) - 32 - self._shift) % 95 + 32) if 32 <= ord(c) < 127 else c
            for c in inner
        )


class CompressionDecorator(DataSourceDecorator):
    """Adds simple RLE compression for runs of repeated characters."""

    def write(self, data: str) -> str:
        compressed = self._rle_encode(data)
        return self._wrapped.write(compressed)

    def read(self, data: str) -> str:
        inner = self._wrapped.read(data)
        return self._rle_decode(inner)

    @staticmethod
    def _rle_encode(data: str) -> str:
        if not data:
            return ""
        result, count, current = [], 1, data[0]
        for c in data[1:]:
            if c == current:
                count += 1
            else:
                result.append(f"{count}{current}" if count > 1 else current)
                current, count = c, 1
        result.append(f"{count}{current}" if count > 1 else current)
        return "".join(result)

    @staticmethod
    def _rle_decode(data: str) -> str:
        result, num = [], ""
        for c in data:
            if c.isdigit():
                num += c
            else:
                count = int(num) if num else 1
                result.append(c * count)
                num = ""
        return "".join(result)


class LoggingDecorator(DataSourceDecorator):
    """Adds logging around read/write operations."""

    def write(self, data: str) -> str:
        print(f"  [LOG] Writing {len(data)} chars")
        result = self._wrapped.write(data)
        print(f"  [LOG] After processing: {len(result)} chars")
        return result

    def read(self, data: str) -> str:
        print(f"  [LOG] Reading {len(data)} chars")
        result = self._wrapped.read(data)
        print(f"  [LOG] After processing: {len(result)} chars")
        return result


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Base source — no processing
    source = StringDataSource()
    print("=== Plain write/read ===")
    written = source.write("Hello, World!")
    print(f"Written: {written}")
    print(f"Read:    {source.read(written)}")

    # Stack decorators: Logging → Encryption → Compression → Base
    # Data flows: write goes outside-in, read goes inside-out
    print("\n=== Decorated: Logging + Encryption + Compression ===")
    decorated = LoggingDecorator(
        EncryptionDecorator(
            CompressionDecorator(StringDataSource()),
            shift=5,
        )
    )

    data = "aaabbbccc Hello World!!!"
    written = decorated.write(data)
    print(f"Original:  {data}")
    print(f"Processed: {written}")

    print("\nReading back:")
    restored = decorated.read(written)
    print(f"Restored:  {restored}")
    print(f"Match:     {data == restored}")

    # You can combine decorators in any order at runtime
    print("\n=== Just Compression + Logging (no encryption) ===")
    simple = LoggingDecorator(CompressionDecorator(StringDataSource()))
    result = simple.write("aaaaaabbbbb test")
    print(f"Compressed: {result}")
