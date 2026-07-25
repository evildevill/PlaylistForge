"""Base classes for export plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from playlistforge.core.enums import ExportFormat
from playlistforge.core.models import ExportOptions, ExportResult, Playlist


class Exporter(ABC):
    """Common interface implemented by all exporters."""

    format: ExportFormat
    label: str
    file_extension: str
    supports_clipboard = False

    @abstractmethod
    def export(
        self,
        playlists: Sequence[Playlist],
        options: ExportOptions,
        destination: Path | None,
    ) -> ExportResult:
        """Export playlists and return a result."""

    def ensure_destination(self, destination: Path | None, options: ExportOptions) -> Path:
        """Resolve and validate a file destination."""
        if destination is not None:
            return destination
        directory = options.destination_directory or Path.cwd()
        filename = options.filename or "playlistforge-export"
        if not filename.endswith(self.file_extension):
            filename = f"{filename}{self.file_extension}"
        return directory / filename
