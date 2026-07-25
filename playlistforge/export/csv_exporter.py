"""CSV exporter."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


class CsvExporter(Exporter):
    """Export selected fields as CSV."""

    format = ExportFormat.CSV
    label = "CSV"
    file_extension = ".csv"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = rows_for_export(playlists, options)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(options.fields))
            writer.writeheader()
            writer.writerows(rows)
        return ExportResult(self.format, path, len(rows), f"Exported {len(rows)} videos to CSV.")
