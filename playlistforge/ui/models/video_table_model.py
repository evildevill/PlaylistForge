"""Qt model for playlist videos."""

from __future__ import annotations

from playlistforge.core.models import Playlist, Video

try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
except ImportError:  # pragma: no cover
    QAbstractTableModel = object  # type: ignore[assignment]
    QModelIndex = object  # type: ignore[assignment]
    Qt = object  # type: ignore[assignment]


class VideoTableModel(QAbstractTableModel):
    """Efficient table model for large playlists."""

    columns = (
        ("lecture", "Lecture Number"),
        ("playlist_index", "Playlist Index"),
        ("title", "Title"),
        ("video_id", "Video ID"),
        ("watch_url", "Watch URL"),
        ("embed_url", "Embed URL"),
        ("thumbnail", "Thumbnail"),
        ("duration", "Duration"),
        ("upload_date", "Upload Date"),
        ("channel", "Channel"),
    )

    def __init__(self) -> None:
        super().__init__()
        self._videos: list[Video] = []

    def set_playlists(self, playlists: tuple[Playlist, ...]) -> None:
        """Replace the model data with videos from the supplied playlists."""
        self.beginResetModel()
        self._videos = [video for playlist in playlists for video in playlist.videos]
        self.endResetModel()

    def videos(self) -> tuple[Video, ...]:
        """Return all model videos."""
        return tuple(self._videos)

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else len(self._videos)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else len(self.columns)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        display_roles = (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole)
        if not index.isValid() or role not in display_roles:
            return None
        video = self._videos[index.row()]
        key = self.columns[index.column()][0]
        value = self._value(video, key)
        return "" if value is None else value

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.columns[section][1]
        return section + 1

    def _value(self, video: Video, key: str) -> object:
        match key:
            case "lecture":
                return video.lecture
            case "playlist_index":
                return video.playlist_index
            case "title":
                return video.display_title
            case "video_id":
                return video.video_id
            case "watch_url":
                return video.watch_url
            case "embed_url":
                return video.embed_url
            case "thumbnail":
                return video.thumbnail
            case "duration":
                return _format_duration(video.duration_seconds)
            case "upload_date":
                return video.upload_date
            case "channel":
                return video.channel
        return None


def _format_duration(seconds: int | None) -> str:
    if seconds is None:
        return ""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
