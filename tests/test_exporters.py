"""Tests for exporters."""

from __future__ import annotations

import json
from pathlib import Path

from playlistforge.core.enums import ClipboardFormat
from playlistforge.core.models import ExportOptions, Playlist, Video
from playlistforge.export.clipboard import format_for_clipboard
from playlistforge.export.csv_exporter import CsvExporter
from playlistforge.export.json_exporter import JsonExporter


def _playlist() -> Playlist:
    return Playlist(
        playlist_id="PL1234567890",
        title="Course",
        channel="Channel",
        webpage_url="https://www.youtube.com/playlist?list=PL1234567890",
        thumbnail=None,
        videos=(
            Video(
                lecture=1,
                playlist_index=1,
                title="Introduction",
                video_id="j8QdcI71-S4",
                watch_url="https://www.youtube.com/watch?v=j8QdcI71-S4",
                embed_url="https://www.youtube.com/embed/j8QdcI71-S4",
                thumbnail="https://i.ytimg.com/vi/j8QdcI71-S4/hqdefault.jpg",
            ),
        ),
    )


def test_json_exporter_writes_selected_fields(tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    options = ExportOptions(fields=("lecture", "title", "videoId"))

    result = JsonExporter().export((_playlist(),), options, path)

    assert result.rows_exported == 1
    assert json.loads(path.read_text(encoding="utf-8")) == [
        {"lecture": 1, "title": "Introduction", "videoId": "j8QdcI71-S4"}
    ]


def test_csv_exporter_escapes_values(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"

    CsvExporter().export((_playlist(),), ExportOptions(fields=("title", "watchUrl")), path)

    assert "Introduction" in path.read_text(encoding="utf-8")


def test_clipboard_urls_only() -> None:
    options = ExportOptions(
        fields=("watchUrl",),
        clipboard_format=ClipboardFormat.URLS_ONLY,
    )

    assert format_for_clipboard((_playlist(),), options) == "https://www.youtube.com/watch?v=j8QdcI71-S4"
