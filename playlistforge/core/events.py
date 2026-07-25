"""Small event objects shared between services and the UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UserMessage:
    """A message safe to show to end users."""

    title: str
    body: str
    technical_details: str | None = None
