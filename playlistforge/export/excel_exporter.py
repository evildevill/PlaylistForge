"""Excel exporter."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


class ExcelExporter(Exporter):
    """Export selected fields as an XLSX workbook."""

    format = ExportFormat.EXCEL
    label = "Excel"
    file_extension = ".xlsx"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        try:
            from openpyxl import Workbook
        except ImportError as exc:
            from playlistforge.core.errors import ExportError

            raise ExportError("openpyxl is required for Excel export.", details=str(exc)) from exc

        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = rows_for_export(playlists, options)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "PlaylistForge"
        sheet.append(list(options.fields))
        for row in rows:
            sheet.append([row.get(field) for field in options.fields])
        workbook.save(path)
        return ExportResult(self.format, path, len(rows), f"Exported {len(rows)} videos to Excel.")
