"""Minimal result type for recoverable operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Result[T]:
    """Represents either a value or a user-facing error string."""

    value: T | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Return whether the operation succeeded."""
        return self.error is None
