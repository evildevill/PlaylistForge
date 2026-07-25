"""Column visibility dialog."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore[assignment, misc]


class ColumnVisibilityDialog(QDialog):
    """Dialog describing configurable table columns."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Columns")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Use the table header context menu to resize and reorder columns."))
