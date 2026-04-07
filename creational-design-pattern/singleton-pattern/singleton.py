"""
Singleton Pattern
=================
Category: Creational Design Pattern

Intent:
    Ensure a class has only ONE instance and provide a global point of access to it.

When to use:
    - When exactly one object is needed to coordinate actions across the system
    - Database connection pools, configuration managers, logging services, thread pools
    - When creating multiple instances would cause conflicts or waste resources

Key Participants:
    - Singleton: The class that maintains a reference to its sole instance
      and provides a class-level method to access it.

Trade-offs:
    + Controlled access to a single instance
    + Reduced memory footprint for shared resources
    - Can make unit testing harder (global state)
    - Violates Single Responsibility Principle (manages own lifecycle + business logic)
"""

import threading


class ConfigurationManager:
    """
    A thread-safe Singleton that manages application configuration.

    Uses double-checked locking to ensure only one instance is created,
    even when multiple threads attempt to access it simultaneously.
    """

    _instance = None
    _lock = threading.Lock()  # Ensures thread-safe instantiation

    def __new__(cls) -> "ConfigurationManager":
        """
        Override __new__ to control instance creation.
        Double-checked locking: first check without lock (fast path),
        then check again inside lock (safe path).
        """
        if cls._instance is None:
            with cls._lock:
                # Second check inside lock prevents race condition where
                # two threads both pass the first check before one acquires the lock.
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        # Prevent re-initialization on subsequent calls to ConfigurationManager()
        if self._initialized:
            return
        self._initialized = True
        self._settings: dict[str, str] = {}
        print("[ConfigurationManager] Initialized (this should appear only once)")

    def set(self, key: str, value: str) -> None:
        """Store a configuration value."""
        self._settings[key] = value

    def get(self, key: str, default: str = "") -> str:
        """Retrieve a configuration value with an optional default."""
        return self._settings.get(key, default)

    def all(self) -> dict[str, str]:
        """Return a copy of all settings."""
        return dict(self._settings)


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Both variables point to the exact same instance
    config_a = ConfigurationManager()
    config_b = ConfigurationManager()

    config_a.set("database_url", "postgres://localhost:5432/mydb")
    config_a.set("log_level", "DEBUG")

    # config_b sees the same data because it IS the same object
    print(f"config_b database_url: {config_b.get('database_url')}")
    print(f"Same instance? {config_a is config_b}")  # True

    # Demonstrate thread safety: spawn threads that all get the same instance
    instances: list[int] = []

    def grab_instance() -> None:
        instances.append(id(ConfigurationManager()))

    threads = [threading.Thread(target=grab_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"All threads got same instance? {len(set(instances)) == 1}")  # True
