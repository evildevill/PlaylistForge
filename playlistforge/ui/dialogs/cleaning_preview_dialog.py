"""Cleaning preview dialog."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore[assignment]


class CleaningPreviewDialog(QDialog):
    """Dialog for cleaning preview summaries."""

    def __init__(self, changed_count: int) -> None:
        super().__init__()
        self.setWindowTitle("Cleaning Preview")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"{changed_count} titles would change."))
