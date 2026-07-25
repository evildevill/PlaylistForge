"""Playlist summary widget."""

from __future__ import annotations

from playlistforge.core.models import Playlist

try:
    from PySide6.QtWidgets import QFormLayout, QLabel, QWidget
except ImportError:  # pragma: no cover
    QWidget = object  # type: ignore[assignment, misc]


class PlaylistSummary(QWidget):
    """Display metadata for the current extraction result."""

    def __init__(self) -> None:
        super().__init__()
        self.title_label = QLabel("No playlist loaded")
        self.channel_label = QLabel("-")
        self.count_label = QLabel("-")
        self.id_label = QLabel("-")
        self.duration_label = QLabel("-")
        self.extraction_time_label = QLabel("-")
        layout = QFormLayout(self)
        layout.addRow("Playlist", self.title_label)
        layout.addRow("Channel", self.channel_label)
        layout.addRow("Video count", self.count_label)
        layout.addRow("Playlist ID", self.id_label)
        layout.addRow("Total duration", self.duration_label)
        layout.addRow("Extraction time", self.extraction_time_label)

    def set_playlist(self, playlist: Playlist | None) -> None:
        """Show playlist metadata."""
        if playlist is None:
            self.title_label.setText("No playlist loaded")
            self.channel_label.setText("-")
            self.count_label.setText("-")
            self.id_label.setText("-")
            self.duration_label.setText("-")
            self.extraction_time_label.setText("-")
            return
        self.title_label.setText(playlist.title)
        self.channel_label.setText(playlist.channel or "-")
        self.count_label.setText(str(playlist.video_count))
        self.id_label.setText(playlist.playlist_id)
        self.duration_label.setText(_format_duration(playlist.total_duration_seconds))
        duration = playlist.extraction_duration_seconds
        self.extraction_time_label.setText("-" if duration is None else f"{duration:.2f}s")


def _format_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"
