"""Parse yt-dlp dictionaries into typed domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from playlistforge.core.enums import VideoAvailability
from playlistforge.core.models import Playlist, Video


def _best_thumbnail(entry: dict[str, Any]) -> str:
    thumbnails = entry.get("thumbnails") or []
    if thumbnails:
        return str(thumbnails[-1].get("url") or "")
    video_id = entry.get("id")
    if video_id:
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    return ""


def _watch_url(video_id: str, fallback: str | None = None) -> str:
    return fallback or f"https://www.youtube.com/watch?v={video_id}"


def _availability(entry: dict[str, Any]) -> VideoAvailability:
    if entry.get("availability") == "private":
        return VideoAvailability.PRIVATE
    if entry.get("availability") == "needs_auth":
        return VideoAvailability.PRIVATE
    if entry.get("is_live"):
        return VideoAvailability.AVAILABLE
    if entry.get("title") in {None, "[Deleted video]", "[Private video]"}:
        title = str(entry.get("title") or "").lower()
        if "private" in title:
            return VideoAvailability.PRIVATE
        if "deleted" in title:
            return VideoAvailability.DELETED
        return VideoAvailability.UNAVAILABLE
    return VideoAvailability.AVAILABLE


def parse_playlist(raw: dict[str, Any], *, duration_seconds: float | None = None) -> Playlist:
    """Convert yt-dlp playlist data into a Playlist model."""
    entries = raw.get("entries") or []
    videos: list[Video] = []
    lecture = 1
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        video_id = str(entry.get("id") or "")
        if not video_id:
            continue
        title = str(entry.get("title") or "Unavailable video")
        url = _watch_url(video_id, entry.get("webpage_url"))
        videos.append(
            Video(
                lecture=lecture,
                playlist_index=index,
                title=title,
                video_id=video_id,
                watch_url=url,
                embed_url=f"https://www.youtube.com/embed/{video_id}",
                thumbnail=_best_thumbnail(entry),
                duration_seconds=entry.get("duration"),
                upload_date=entry.get("upload_date"),
                channel=entry.get("channel") or entry.get("uploader"),
                availability=_availability(entry),
            )
        )
        lecture += 1

    playlist_id = str(raw.get("id") or raw.get("playlist_id") or "")
    playlist_thumbnail = _best_thumbnail(raw) or None
    return Playlist(
        playlist_id=playlist_id,
        title=str(raw.get("title") or "Untitled playlist"),
        channel=raw.get("channel") or raw.get("uploader"),
        webpage_url=str(raw.get("webpage_url") or f"https://www.youtube.com/playlist?list={playlist_id}"),
        thumbnail=playlist_thumbnail,
        videos=tuple(videos),
        extracted_at=datetime.now(UTC),
        extraction_duration_seconds=duration_seconds,
    )
