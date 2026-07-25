"""Qt model for playlist summaries."""

from __future__ import annotations

from playlistforge.core.models import Playlist

try:
    from PySide6.QtCore import QAbstractListModel, QModelIndex, QPersistentModelIndex, Qt
except ImportError:  # pragma: no cover
    QAbstractListModel = object  # type: ignore[assignment, misc]
    QModelIndex = object  # type: ignore[assignment, misc]
    QPersistentModelIndex = object  # type: ignore[assignment, misc]
    Qt = object  # type: ignore[assignment, misc]


class PlaylistListModel(QAbstractListModel):
    """List model for extracted playlists."""

    def __init__(self) -> None:
        super().__init__()
        self._playlists: list[Playlist] = []

    def set_playlists(self, playlists: tuple[Playlist, ...]) -> None:
        """Replace playlists."""
        self.beginResetModel()
        self._playlists = list(playlists)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else len(self._playlists)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        playlist = self._playlists[index.row()]
        return f"{playlist.title} ({playlist.video_count})"
