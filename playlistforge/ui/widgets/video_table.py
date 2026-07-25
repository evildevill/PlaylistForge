"""Video preview table."""

from __future__ import annotations

try:
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QAbstractItemView, QApplication, QMenu, QTableView
except ImportError:  # pragma: no cover
    QPoint = object  # type: ignore[assignment]
    QTableView = object  # type: ignore[assignment]


class VideoTable(QTableView):
    """Configured video preview table."""

    def __init__(self) -> None:
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setMinimumSectionSize(90)
        self.verticalHeader().setVisible(False)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position: QPoint) -> None:
        menu = QMenu(self)
        copy_action = QAction("Copy selected rows", self)
        copy_action.triggered.connect(self.copy_selected)
        resize_action = QAction("Resize columns to contents", self)
        resize_action.triggered.connect(self.resizeColumnsToContents)
        menu.addAction(copy_action)
        menu.addAction(resize_action)
        menu.exec(self.viewport().mapToGlobal(position))

    def copy_selected(self) -> None:
        """Copy selected cells as tab-separated text."""
        indexes = sorted(self.selectedIndexes(), key=lambda index: (index.row(), index.column()))
        if not indexes:
            return
        rows: dict[int, list[str]] = {}
        for index in indexes:
            rows.setdefault(index.row(), []).append(str(index.data() or ""))
        text = "\n".join("\t".join(values) for _, values in sorted(rows.items()))
        QApplication.clipboard().setText(text)
