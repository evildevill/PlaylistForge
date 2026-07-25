"""Recent, history, and favorites panel."""

from __future__ import annotations

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import QListWidget, QTabWidget, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    Signal = object  # type: ignore[assignment, misc]
    QWidget = object  # type: ignore[assignment, misc]


class HistoryPanel(QWidget):
    """Sidebar showing recent and favorite playlists."""

    url_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.recent_list = QListWidget()
        self.favorite_list = QListWidget()
        self.history_list = QListWidget()
        tabs = QTabWidget()
        tabs.addTab(self.recent_list, "Recent")
        tabs.addTab(self.favorite_list, "Favorites")
        tabs.addTab(self.history_list, "History")
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.recent_list.itemDoubleClicked.connect(
            lambda item: self.url_selected.emit(item.text())
        )
        self.favorite_list.itemDoubleClicked.connect(
            lambda item: self.url_selected.emit(item.text())
        )

    def set_recent(self, urls: tuple[str, ...]) -> None:
        """Replace recent URLs."""
        self.recent_list.clear()
        self.recent_list.addItems(list(urls))

    def set_favorites(self, urls: tuple[str, ...]) -> None:
        """Replace favorite URLs."""
        self.favorite_list.clear()
        self.favorite_list.addItems(list(urls))
