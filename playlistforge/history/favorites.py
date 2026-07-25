"""Favorite playlist helpers."""

from __future__ import annotations

from dataclasses import replace

from playlistforge.core.models import ApplicationSettings


def toggle_favorite(settings: ApplicationSettings, url: str) -> ApplicationSettings:
    """Return settings with a favorite URL toggled."""
    favorites = list(settings.favorites)
    if url in favorites:
        favorites.remove(url)
    else:
        favorites.insert(0, url)
    return replace(settings, favorites=tuple(favorites))
