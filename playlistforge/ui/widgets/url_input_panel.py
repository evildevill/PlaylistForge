"""Playlist URL entry panel."""

from __future__ import annotations

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    Signal = object  # type: ignore[assignment, misc]
    QWidget = object  # type: ignore[assignment, misc]


class UrlInputPanel(QWidget):
    """Large URL input area with primary extraction controls."""

    extract_requested = Signal(str)
    paste_requested = Signal()
    cancel_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.url_input = QPlainTextEdit()
        self.url_input.setPlaceholderText("Paste one or many YouTube playlist URLs...")
        self.url_input.setMinimumHeight(92)
        self.paste_button = QPushButton("Paste")
        self.extract_button = QPushButton("Extract")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.paste_button)
        buttons.addWidget(self.extract_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.url_input)
        layout.addLayout(buttons)

        self.paste_button.clicked.connect(self.paste_requested.emit)
        self.extract_button.clicked.connect(
            lambda: self.extract_requested.emit(self.url_input.toPlainText())
        )
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

    def set_busy(self, busy: bool) -> None:
        """Toggle busy UI state."""
        self.extract_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)
