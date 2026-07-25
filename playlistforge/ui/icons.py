"""Icon helpers."""

from __future__ import annotations

try:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QStyle
except ImportError:  # pragma: no cover
    QApplication = object  # type: ignore[assignment, misc]
    QIcon = object  # type: ignore[assignment, misc]
    QStyle = object  # type: ignore[assignment, misc]


def standard_icon(pixmap: QStyle.StandardPixmap) -> QIcon:
    """Return a platform standard icon."""
    return QApplication.style().standardIcon(pixmap)
