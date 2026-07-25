"""HTML exporter."""

from __future__ import annotations

import html
from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist
from playlistforge.export.base import Exporter
from playlistforge.export.fields import rows_for_export


class HtmlExporter(Exporter):
    """Export selected fields as a standalone HTML table."""

    format = ExportFormat.HTML
    label = "HTML"
    file_extension = ".html"

    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        path = self.ensure_destination(destination, options)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = rows_for_export(playlists, options)
        headers = "".join(f"<th>{html.escape(field)}</th>" for field in options.fields)
        body = []
        for row in rows:
            cells = "".join(
                f"<td>{html.escape(str(row.get(field) or ''))}</td>"
                for field in options.fields
            )
            body.append(f"<tr>{cells}</tr>")
        document = (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            "<title>PlaylistForge Export</title>"
            "<style>body{font-family:system-ui,sans-serif;margin:32px}"
            "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;"
            "padding:8px;text-align:left}th{background:#f4f4f4}</style></head>"
            f"<body><h1>PlaylistForge Export</h1><table><thead><tr>{headers}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody></table></body></html>"
        )
        path.write_text(document, encoding="utf-8")
        return ExportResult(self.format, path, len(rows), f"Exported {len(rows)} videos to HTML.")
