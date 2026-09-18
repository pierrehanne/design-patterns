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
    """One process-local configuration instance, initialized before publication.

    The creation lock protects publication; the settings lock protects access.
    Neither lock turns several separate get/set calls into a transaction.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "ConfigurationManager":
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._settings: dict[str, str] = {}
                instance._settings_lock = threading.Lock()
                # Publish only after every field is ready for concurrent callers.
                cls._instance = instance
                print("[ConfigurationManager] Initialized (this should appear only once)")
            return cls._instance

    def set(self, key: str, value: str) -> None:
        """Store a configuration value."""
        with self._settings_lock:
            self._settings[key] = value

    def get(self, key: str, default: str = "") -> str:
        """Retrieve a configuration value with an optional default."""
        with self._settings_lock:
            return self._settings.get(key, default)

    def all(self) -> dict[str, str]:
        """Return a snapshot rather than exposing shared mutable state."""
        with self._settings_lock:
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
