"""Plain text exporter."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


class TxtExporter(Exporter):
    """Export selected fields as readable text."""

    format = ExportFormat.TXT
    label = "Text"
    file_extension = ".txt"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for row in rows_for_export(playlists, options):
            lines.append(" | ".join("" if value is None else str(value) for value in row.values()))
        path.write_text("\n".join(lines), encoding="utf-8")
        return ExportResult(self.format, path, len(lines), f"Exported {len(lines)} videos to text.")
