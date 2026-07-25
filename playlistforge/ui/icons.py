"""Icon helpers."""

from __future__ import annotations

try:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QStyle
except ImportError:  # pragma: no cover
    QApplication = object  # type: ignore[assignment]
    QIcon = object  # type: ignore[assignment]
    QStyle = object  # type: ignore[assignment]


def standard_icon(pixmap: QStyle.StandardPixmap) -> QIcon:
    """Return a platform standard icon."""
    return QApplication.style().standardIcon(pixmap)
