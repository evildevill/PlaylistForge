"""In-memory history helpers backed by application settings."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from playlistforge.core.models import ApplicationSettings, HistoryItem, Playlist


def history_item_from_playlist(playlist: Playlist, *, favorite: bool = False) -> HistoryItem:
    """Create a history item from a playlist."""
    return HistoryItem(
        playlist_id=playlist.playlist_id,
        title=playlist.title,
        url=playlist.webpage_url,
        channel=playlist.channel,
        extracted_at=datetime.now(UTC),
        video_count=playlist.video_count,
        favorite=favorite,
    )


def add_recent_playlist(
    settings: ApplicationSettings,
    url: str,
    *,
    limit: int = 20,
) -> ApplicationSettings:
    """Return settings with a URL moved to the top of recent playlists."""
    urls = [item for item in settings.recent_playlists if item != url]
    urls.insert(0, url)
    return replace(settings, recent_playlists=tuple(urls[:limit]))
