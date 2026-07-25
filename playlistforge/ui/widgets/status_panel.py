"""Status/progress panel."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    QWidget = object  # type: ignore[assignment]


class StatusPanel(QWidget):
    """Status text and progress bar."""

    def __init__(self) -> None:
        super().__init__()
        self.label = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)

    def set_status(self, message: str, percent: int = 0) -> None:
        """Update status message and progress percent."""
        self.label.setText(message)
        self.progress.setValue(percent)
