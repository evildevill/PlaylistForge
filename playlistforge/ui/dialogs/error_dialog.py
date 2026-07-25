"""User-friendly error dialog."""

from __future__ import annotations

from playlistforge.core.errors import PlaylistForgeError

try:
    from PySide6.QtWidgets import QMessageBox, QWidget
except ImportError:  # pragma: no cover
    QMessageBox = object  # type: ignore[assignment]
    QWidget = object  # type: ignore[assignment]


def show_error(parent: QWidget, error: BaseException) -> None:
    """Show an error without exposing tracebacks."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle("PlaylistForge")
    if isinstance(error, PlaylistForgeError):
        box.setText(error.user_message)
        if error.details:
            box.setDetailedText(error.details)
    else:
        box.setText("Something unexpected happened. The details were written to the log.")
    box.exec()
