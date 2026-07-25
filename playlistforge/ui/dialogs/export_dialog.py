"""Export path dialog helpers."""

from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtWidgets import QFileDialog, QWidget
except ImportError:  # pragma: no cover
    QFileDialog = object  # type: ignore[assignment]
    QWidget = object  # type: ignore[assignment]


def choose_export_path(parent: QWidget, extension: str, directory: Path | None) -> Path | None:
    """Prompt for an export destination."""
    start = str(directory or Path.home())
    path, _ = QFileDialog.getSaveFileName(parent, "Export playlist", start, f"*{extension}")
    return Path(path) if path else None
