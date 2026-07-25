"""JSON exporter."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


class JsonExporter(Exporter):
    """Export selected fields as JSON."""

    format = ExportFormat.JSON
    label = "JSON"
    file_extension = ".json"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = rows_for_export(playlists, options)
        indent = 2 if options.pretty_json else None
        path.write_text(json.dumps(rows, indent=indent, ensure_ascii=False), encoding="utf-8")
        return ExportResult(self.format, path, len(rows), f"Exported {len(rows)} videos to JSON.")
