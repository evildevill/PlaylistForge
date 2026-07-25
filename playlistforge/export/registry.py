"""Exporter registry."""

from __future__ import annotations

from playlistforge.core.enums import ExportFormat
from playlistforge.export.base import Exporter
from playlistforge.export.csv_exporter import CsvExporter
from playlistforge.export.excel_exporter import ExcelExporter
from playlistforge.export.html_exporter import HtmlExporter
from playlistforge.export.json_exporter import JsonExporter
from playlistforge.export.markdown_exporter import MarkdownExporter
from playlistforge.export.txt_exporter import TxtExporter


class ExporterRegistry:
    """Discover and retrieve registered exporters."""

    def __init__(self) -> None:
        self._exporters: dict[ExportFormat, Exporter] = {}

    def register(self, exporter: Exporter) -> None:
        """Register an exporter instance."""
        self._exporters[exporter.format] = exporter

    def get(self, export_format: ExportFormat) -> Exporter:
        """Return an exporter by format."""
        return self._exporters[export_format]

    def all(self) -> tuple[Exporter, ...]:
        """Return all registered exporters."""
        return tuple(self._exporters.values())


def default_exporter_registry() -> ExporterRegistry:
    """Return the default exporter registry."""
    registry = ExporterRegistry()
    for exporter in (
        JsonExporter(),
        TxtExporter(),
        CsvExporter(),
        MarkdownExporter(),
        HtmlExporter(),
        ExcelExporter(),
    ):
        registry.register(exporter)
    return registry
