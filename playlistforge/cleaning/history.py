"""Undo stack for cleaning operations."""

from __future__ import annotations

from playlistforge.core.models import Playlist


class CleaningHistory:
    """Small in-memory undo stack for playlist cleaning."""

    def __init__(self, limit: int = 20) -> None:
        self._limit = limit
        self._items: list[Playlist] = []

    def push(self, playlist: Playlist) -> None:
        """Push a playlist snapshot."""
        self._items.append(playlist)
        if len(self._items) > self._limit:
            self._items.pop(0)

    def pop(self) -> Playlist | None:
        """Return the most recent snapshot if available."""
        if not self._items:
            return None
        return self._items.pop()
