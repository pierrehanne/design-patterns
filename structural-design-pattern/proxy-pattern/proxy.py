"""
Proxy Pattern
=============
Category: Structural Design Pattern

Intent:
    Provide a surrogate or placeholder for another object to control access to it.
    The proxy has the same interface as the real object, so clients can't tell
    the difference.

When to use:
    - Caching Proxy: Cache expensive operation results to avoid repeated computation
    - Virtual Proxy: Lazy-load a heavy resource only when actually needed
    - Protection Proxy: Control access based on permissions
    - Logging Proxy: Add logging/monitoring without modifying the real service

Key Participants:
    - Subject (interface): Common interface for Real and Proxy
    - RealSubject: The actual object that does the work
    - Proxy: Controls access to the RealSubject, same interface
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import wraps


# ---------------------------------------------------------------------------
# Subject interface
# ---------------------------------------------------------------------------
class WeatherService(ABC):
    """Interface for fetching weather data."""

    @abstractmethod
    def get_forecast(self, city: str) -> dict:
        ...

    @abstractmethod
    def get_temperature(self, city: str) -> float:
        ...


# ---------------------------------------------------------------------------
# Real Subject — the actual expensive service
# ---------------------------------------------------------------------------
class RealWeatherService(WeatherService):
    """
    Simulates an expensive external API call.
    Each call takes "time" and costs API quota.
    """

    def __init__(self) -> None:
        self.call_count = 0

    def get_forecast(self, city: str) -> dict:
        self.call_count += 1
        print(f"    [RealService] API call #{self.call_count} — fetching forecast for {city}")
        return {
            "city": city,
            "conditions": "Partly Cloudy",
            "high": 72,
            "low": 58,
            "humidity": 45,
        }

    def get_temperature(self, city: str) -> float:
        self.call_count += 1
        print(f"    [RealService] API call #{self.call_count} — fetching temperature for {city}")
        return 68.5


# ---------------------------------------------------------------------------
# Caching Proxy — caches results to avoid redundant API calls
# ---------------------------------------------------------------------------
class CachingWeatherProxy(WeatherService):
    """
    Caches responses for a configurable TTL. Identical requests within the TTL
    return cached data instead of hitting the real service.
    """

    def __init__(self, real_service: WeatherService, ttl_seconds: int = 60) -> None:
        self._service = real_service
        self._ttl = timedelta(seconds=ttl_seconds)
        self._cache: dict[str, tuple[datetime, any]] = {}

    def _get_cached(self, key: str):
        if key in self._cache:
            timestamp, value = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                print(f"    [Cache HIT] {key}")
                return value
            else:
                print(f"    [Cache EXPIRED] {key}")
                del self._cache[key]
        else:
            print(f"    [Cache MISS] {key}")
        return None

    def _set_cached(self, key: str, value) -> None:
        self._cache[key] = (datetime.now(), value)

    def get_forecast(self, city: str) -> dict:
        key = f"forecast:{city}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        result = self._service.get_forecast(city)
        self._set_cached(key, result)
        return result

    def get_temperature(self, city: str) -> float:
        key = f"temp:{city}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        result = self._service.get_temperature(city)
        self._set_cached(key, result)
        return result


# ---------------------------------------------------------------------------
# Access Control Proxy — restricts access based on API key
# ---------------------------------------------------------------------------
class AccessControlWeatherProxy(WeatherService):
    """
    Checks that the caller has a valid API key before forwarding the request.
    This is the Protection Proxy variant.
    """

    VALID_KEYS = {"key-alice-123", "key-bob-456"}

    def __init__(self, real_service: WeatherService, api_key: str) -> None:
        self._service = real_service
        self._api_key = api_key

    def _check_access(self) -> None:
        if self._api_key not in self.VALID_KEYS:
            raise PermissionError(f"Invalid API key: {self._api_key}")

    def get_forecast(self, city: str) -> dict:
        self._check_access()
        return self._service.get_forecast(city)

    def get_temperature(self, city: str) -> float:
        self._check_access()
        return self._service.get_temperature(city)


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    real = RealWeatherService()

    # --- Caching Proxy Demo ---
    print("=== Caching Proxy ===")
    cached = CachingWeatherProxy(real, ttl_seconds=300)

    # First call — cache miss, hits real service
    print("\nFirst request:")
    forecast = cached.get_forecast("New York")
    print(f"  Result: {forecast}")

    # Second call — cache hit, returns cached data
    print("\nSecond request (same city):")
    forecast = cached.get_forecast("New York")
    print(f"  Result: {forecast}")

    # Different city — cache miss
    print("\nDifferent city:")
    forecast = cached.get_forecast("London")
    print(f"  Result: {forecast}")

    print(f"\nReal service was called {real.call_count} times (not 3)")

    # --- Access Control Proxy Demo ---
    print("\n=== Access Control Proxy ===")
    real2 = RealWeatherService()

    # Valid key
    print("\nValid API key:")
    auth_service = AccessControlWeatherProxy(real2, "key-alice-123")
    temp = auth_service.get_temperature("Paris")
    print(f"  Temperature: {temp}")

    # Invalid key
    print("\nInvalid API key:")
    bad_service = AccessControlWeatherProxy(real2, "key-hacker-999")
    try:
        bad_service.get_temperature("Paris")
    except PermissionError as e:
        print(f"  Access denied: {e}")
