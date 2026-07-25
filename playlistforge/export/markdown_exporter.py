"""Markdown exporter."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


def _escape(value: object) -> str:
    return str(value or "").replace("|", "\\|")


class MarkdownExporter(Exporter):
    """Export selected fields as a Markdown table."""

    format = ExportFormat.MARKDOWN
    label = "Markdown"
    file_extension = ".md"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = rows_for_export(playlists, options)
        header = "| " + " | ".join(options.fields) + " |"
        separator = "| " + " | ".join("---" for _ in options.fields) + " |"
        body = [
            "| " + " | ".join(_escape(row.get(field)) for field in options.fields) + " |"
            for row in rows
        ]
        path.write_text("\n".join([header, separator, *body]), encoding="utf-8")
        return ExportResult(
            self.format,
            path,
            len(rows),
            f"Exported {len(rows)} videos to Markdown.",
        )
