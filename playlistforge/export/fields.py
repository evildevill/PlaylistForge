"""Export field definitions and row mapping."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from playlistforge.core.models import ExportField, ExportOptions, Playlist, Video

DEFAULT_EXPORT_FIELDS: tuple[ExportField, ...] = (
    ExportField("lecture", "Lecture"),
    ExportField("playlistIndex", "Playlist Index"),
    ExportField("title", "Title"),
    ExportField("videoId", "Video ID"),
    ExportField("watchUrl", "Watch URL"),
    ExportField("embedUrl", "Embed URL"),
    ExportField("thumbnail", "Thumbnail"),
    ExportField("duration", "Duration"),
    ExportField("uploadDate", "Upload Date"),
    ExportField("channel", "Channel"),
    ExportField("playlistId", "Playlist ID"),
)


def iter_videos(playlists: Iterable[Playlist]) -> Iterable[tuple[Playlist, Video]]:
    """Yield playlist/video pairs."""
    for playlist in playlists:
        for video in playlist.videos:
            yield playlist, video


def video_to_row(playlist: Playlist, video: Video, options: ExportOptions) -> dict[str, Any]:
    """Convert a video to a selectable export row."""
    title = video.display_title if options.use_cleaned_titles else video.title
    row = {
        "lecture": video.lecture,
        "playlistIndex": video.playlist_index,
        "title": title,
        "videoId": video.video_id,
        "watchUrl": video.watch_url,
        "embedUrl": video.embed_url,
        "thumbnail": video.thumbnail,
        "duration": video.duration_seconds,
        "uploadDate": video.upload_date,
        "channel": video.channel,
        "playlistId": playlist.playlist_id,
    }
    return {field: row.get(field) for field in options.fields}


def rows_for_export(playlists: Iterable[Playlist], options: ExportOptions) -> list[dict[str, Any]]:
    """Return selected export rows."""
    return [video_to_row(playlist, video, options) for playlist, video in iter_videos(playlists)]
