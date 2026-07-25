"""Thumbnail display widget."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QLabel
except ImportError:  # pragma: no cover
    QLabel = object  # type: ignore[assignment]


class ThumbnailLabel(QLabel):
    """Simple thumbnail placeholder; image cache can extend this later."""

    def __init__(self) -> None:
        super().__init__("Thumbnail")
        self.setMinimumSize(160, 90)
        self.setScaledContents(True)
