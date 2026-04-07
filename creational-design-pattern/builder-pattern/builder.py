"""
Builder Pattern
================
Category: Creational Design Pattern

Intent:
    Separate the construction of a complex object from its representation,
    allowing the same construction process to create different representations.
    Especially useful when an object has many optional parameters.

When to use:
    - When a constructor would need 5+ parameters (telescoping constructor problem)
    - When you want to create different representations of the same product
    - When construction involves multiple steps that should be chainable
    - When some parameters are optional and you want clear, readable construction

Key Participants:
    - Builder: Provides a fluent API with method chaining for step-by-step construction
    - Product: The complex object being built
    - Director (optional): Defines preset construction sequences

Why Builder over constructor with many params:
    - Named methods are self-documenting (`.with_timeout(30)` vs positional arg `30`)
    - Optional params don't require None/null placeholders
    - Validation can happen at build time, not scattered across setters
"""

from dataclasses import dataclass, field
from typing import Self


# ---------------------------------------------------------------------------
# Product — the complex object we're building
# ---------------------------------------------------------------------------
@dataclass(frozen=True)  # Immutable once built
class HttpRequest:
    """Represents a fully configured HTTP request."""
    method: str
    url: str
    headers: dict[str, str]
    query_params: dict[str, str]
    body: str | None
    timeout_seconds: int
    retries: int
    follow_redirects: bool

    def __str__(self) -> str:
        parts = [f"{self.method} {self.url}"]
        if self.query_params:
            qs = "&".join(f"{k}={v}" for k, v in self.query_params.items())
            parts[0] += f"?{qs}"
        for k, v in self.headers.items():
            parts.append(f"  {k}: {v}")
        if self.body:
            parts.append(f"  Body: {self.body[:80]}...")
        parts.append(f"  Timeout: {self.timeout_seconds}s | Retries: {self.retries} | Follow redirects: {self.follow_redirects}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Builder — fluent API with method chaining
# ---------------------------------------------------------------------------
class HttpRequestBuilder:
    """
    Builds an HttpRequest step by step. Each method returns `self`
    to enable chaining: HttpRequestBuilder().get(url).header(...).build()
    """

    def __init__(self) -> None:
        self._method: str = "GET"
        self._url: str = ""
        self._headers: dict[str, str] = {}
        self._query_params: dict[str, str] = {}
        self._body: str | None = None
        self._timeout: int = 30
        self._retries: int = 0
        self._follow_redirects: bool = True

    # --- HTTP method shortcuts ---
    def get(self, url: str) -> Self:
        self._method = "GET"
        self._url = url
        return self

    def post(self, url: str) -> Self:
        self._method = "POST"
        self._url = url
        return self

    def put(self, url: str) -> Self:
        self._method = "PUT"
        self._url = url
        return self

    def delete(self, url: str) -> Self:
        self._method = "DELETE"
        self._url = url
        return self

    # --- Configuration methods (each returns self for chaining) ---
    def header(self, key: str, value: str) -> Self:
        self._headers[key] = value
        return self

    def query(self, key: str, value: str) -> Self:
        self._query_params[key] = value
        return self

    def body(self, content: str) -> Self:
        self._body = content
        return self

    def timeout(self, seconds: int) -> Self:
        self._timeout = seconds
        return self

    def retries(self, count: int) -> Self:
        self._retries = count
        return self

    def no_follow_redirects(self) -> Self:
        self._follow_redirects = False
        return self

    # --- Build: validate and produce the immutable product ---
    def build(self) -> HttpRequest:
        if not self._url:
            raise ValueError("URL is required")
        if self._method in ("POST", "PUT") and self._body is None:
            raise ValueError(f"{self._method} requests should have a body")
        if self._timeout < 0:
            raise ValueError("Timeout must be non-negative")

        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=dict(self._headers),
            query_params=dict(self._query_params),
            body=self._body,
            timeout_seconds=self._timeout,
            retries=self._retries,
            follow_redirects=self._follow_redirects,
        )


# ---------------------------------------------------------------------------
# Director (optional) — presets for common request configurations
# ---------------------------------------------------------------------------
class RequestDirector:
    """Provides pre-configured builder sequences for common use cases."""

    @staticmethod
    def json_api_get(url: str) -> HttpRequestBuilder:
        return (
            HttpRequestBuilder()
            .get(url)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json")
            .timeout(10)
            .retries(3)
        )

    @staticmethod
    def authenticated_post(url: str, token: str, body: str) -> HttpRequestBuilder:
        return (
            HttpRequestBuilder()
            .post(url)
            .header("Authorization", f"Bearer {token}")
            .header("Content-Type", "application/json")
            .body(body)
            .timeout(30)
        )


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Manual step-by-step building with chaining
    request = (
        HttpRequestBuilder()
        .get("https://api.example.com/users")
        .header("Authorization", "Bearer abc123")
        .query("page", "1")
        .query("limit", "50")
        .timeout(15)
        .retries(2)
        .build()
    )
    print("Manual build:")
    print(request)

    # Using the Director for a preset configuration
    print("\nDirector preset (JSON API GET):")
    api_request = (
        RequestDirector.json_api_get("https://api.example.com/products")
        .query("category", "electronics")
        .build()
    )
    print(api_request)

    print("\nDirector preset (Authenticated POST):")
    post_request = (
        RequestDirector.authenticated_post(
            "https://api.example.com/orders",
            "secret-token",
            '{"item": "laptop", "qty": 1}',
        )
        .build()
    )
    print(post_request)
