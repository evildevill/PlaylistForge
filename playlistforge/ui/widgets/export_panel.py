"""Export controls."""

from __future__ import annotations

from playlistforge.core.enums import ExportFormat

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QPushButton, QVBoxLayout
except ImportError:  # pragma: no cover
    Signal = object  # type: ignore[assignment, misc]
    QGroupBox = object  # type: ignore[assignment, misc]


class ExportPanel(QGroupBox):
    """Panel for export configuration."""

    export_requested = Signal(str)
    copy_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Export")
        self.format_combo = QComboBox()
        for export_format in (
            ExportFormat.JSON,
            ExportFormat.TXT,
            ExportFormat.CSV,
            ExportFormat.MARKDOWN,
            ExportFormat.HTML,
            ExportFormat.EXCEL,
        ):
            self.format_combo.addItem(export_format.value.upper(), export_format.value)
        self.pretty_json = QCheckBox("Pretty JSON")
        self.pretty_json.setChecked(True)
        self.cleaned_titles = QCheckBox("Use cleaned titles")
        self.cleaned_titles.setChecked(True)
        self.export_button = QPushButton("Export file")
        self.copy_button = QPushButton("Copy")

        layout = QVBoxLayout(self)
        layout.addWidget(self.format_combo)
        layout.addWidget(self.pretty_json)
        layout.addWidget(self.cleaned_titles)
        layout.addWidget(self.export_button)
        layout.addWidget(self.copy_button)

        self.export_button.clicked.connect(
            lambda: self.export_requested.emit(str(self.format_combo.currentData()))
        )
        self.copy_button.clicked.connect(self.copy_requested.emit)
