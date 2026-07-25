"""Proxy models for sorting and filtering."""

from __future__ import annotations

try:
    from PySide6.QtCore import QSortFilterProxyModel, Qt
except ImportError:  # pragma: no cover
    QSortFilterProxyModel = object  # type: ignore[assignment]
    Qt = object  # type: ignore[assignment]


class VideoFilterProxyModel(QSortFilterProxyModel):
    """Case-insensitive search across all visible video columns."""

    def __init__(self) -> None:
        super().__init__()
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(-1)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
