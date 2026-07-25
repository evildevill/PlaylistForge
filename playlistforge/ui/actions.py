"""Application actions."""

from __future__ import annotations

try:
    from PySide6.QtGui import QAction, QKeySequence
    from PySide6.QtWidgets import QWidget
except ImportError:  # pragma: no cover
    QAction = object  # type: ignore[assignment, misc]
    QKeySequence = object  # type: ignore[assignment, misc]
    QWidget = object  # type: ignore[assignment, misc]


def action(parent: QWidget, text: str, shortcut: str | None = None) -> QAction:
    """Create a QAction with an optional shortcut."""
    created = QAction(text, parent)
    if shortcut:
        created.setShortcut(QKeySequence(shortcut))
    return created
