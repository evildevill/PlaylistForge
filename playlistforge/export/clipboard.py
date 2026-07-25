"""Clipboard-oriented formatting helpers."""

from __future__ import annotations

from collections.abc import Sequence

from playlistforge.core.enums import ClipboardFormat
from playlistforge.core.models import ExportOptions, Playlist
from playlistforge.export.fields import rows_for_export


def format_for_clipboard(playlists: Sequence[Playlist], options: ExportOptions) -> str:
    """Return clipboard text for the selected clipboard mode."""
    rows = rows_for_export(playlists, options)
    match options.clipboard_format:
        case ClipboardFormat.URLS_ONLY:
            return "\n".join(str(row.get("watchUrl") or "") for row in rows)
        case ClipboardFormat.EMBED_URLS_ONLY:
            return "\n".join(str(row.get("embedUrl") or "") for row in rows)
        case ClipboardFormat.IDS_ONLY:
            return "\n".join(str(row.get("videoId") or "") for row in rows)
        case ClipboardFormat.TITLES_ONLY:
            return "\n".join(str(row.get("title") or "") for row in rows)
        case ClipboardFormat.ALL_FIELDS:
            return "\n".join("\t".join(str(value or "") for value in row.values()) for row in rows)
