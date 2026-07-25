"""Typed domain models for PlaylistForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from playlistforge.core.enums import (
    CleaningRuleType,
    ClipboardFormat,
    ExportFormat,
    ExportMode,
    ExtractionStatus,
    ThemeMode,
    VideoAvailability,
)


@dataclass(slots=True, frozen=True)
class Video:
    """A single video inside a playlist."""

    lecture: int
    playlist_index: int
    title: str
    video_id: str
    watch_url: str
    embed_url: str
    thumbnail: str
    duration_seconds: int | None = None
    upload_date: str | None = None
    channel: str | None = None
    availability: VideoAvailability = VideoAvailability.UNKNOWN
    title_cleaned: str | None = None

    @property
    def display_title(self) -> str:
        """Return the cleaned title when available, otherwise the original title."""
        return self.title_cleaned or self.title


@dataclass(slots=True, frozen=True)
class Playlist:
    """A YouTube playlist and its extracted videos."""

    playlist_id: str
    title: str
    channel: str | None
    webpage_url: str
    thumbnail: str | None
    videos: tuple[Video, ...]
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    extraction_duration_seconds: float | None = None

    @property
    def video_count(self) -> int:
        """Return the number of parsed videos."""
        return len(self.videos)

    @property
    def total_duration_seconds(self) -> int:
        """Return the total known duration for available videos."""
        return sum(video.duration_seconds or 0 for video in self.videos)


@dataclass(slots=True, frozen=True)
class ExportField:
    """A selectable field in exported output."""

    key: str
    label: str
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class ExportOptions:
    """Options used by exporters."""

    format: ExportFormat = ExportFormat.JSON
    fields: tuple[str, ...] = (
        "lecture",
        "title",
        "videoId",
        "watchUrl",
        "embedUrl",
        "thumbnail",
    )
    mode: ExportMode = ExportMode.INDIVIDUAL
    clipboard_format: ClipboardFormat = ClipboardFormat.ALL_FIELDS
    include_playlist_metadata: bool = False
    use_cleaned_titles: bool = True
    pretty_json: bool = True
    destination_directory: Path | None = None
    filename: str | None = None


@dataclass(slots=True, frozen=True)
class CleaningRule:
    """A serializable cleaning rule definition."""

    name: str
    rule_type: CleaningRuleType
    enabled: bool = True
    pattern: str = ""
    replacement: str = ""
    case_sensitive: bool = False


@dataclass(slots=True, frozen=True)
class CleaningPreset:
    """A named collection of cleaning rules."""

    name: str
    rules: tuple[CleaningRule, ...]


@dataclass(slots=True, frozen=True)
class CleaningRules:
    """The active cleaning configuration."""

    rules: tuple[CleaningRule, ...] = ()
    active_preset: str | None = None


@dataclass(slots=True, frozen=True)
class HistoryItem:
    """A previously extracted playlist reference."""

    playlist_id: str
    title: str
    url: str
    channel: str | None
    extracted_at: datetime
    video_count: int
    favorite: bool = False


@dataclass(slots=True, frozen=True)
class ApplicationSettings:
    """Persistent user settings."""

    theme: ThemeMode = ThemeMode.SYSTEM
    window_width: int = 1280
    window_height: int = 820
    last_export_directory: Path | None = None
    recent_playlists: tuple[str, ...] = ()
    favorites: tuple[str, ...] = ()
    cleaning: CleaningRules = field(default_factory=CleaningRules)
    export_options: ExportOptions = field(default_factory=ExportOptions)
    last_filename: str = "playlistforge-export"
    visible_columns: tuple[str, ...] = (
        "lecture",
        "playlist_index",
        "title",
        "video_id",
        "watch_url",
        "embed_url",
        "thumbnail",
        "duration",
        "upload_date",
        "channel",
    )
    column_widths: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ExtractionRequest:
    """A request to extract one or more playlist URLs."""

    urls: tuple[str, ...]
    retry_count: int = 2
    timeout_seconds: int = 30


@dataclass(slots=True, frozen=True)
class ExtractionProgress:
    """Progress emitted by the extraction layer."""

    status: ExtractionStatus
    message: str
    current: int = 0
    total: int = 0
    url: str | None = None

    @property
    def percent(self) -> int:
        """Return integer progress percent."""
        if self.total <= 0:
            return 0
        return max(0, min(100, int((self.current / self.total) * 100)))


@dataclass(slots=True, frozen=True)
class ExtractionResult:
    """Successful extraction result."""

    playlists: tuple[Playlist, ...]
    warnings: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class ExportResult:
    """Result returned by an exporter."""

    format: ExportFormat
    destination: Path | None
    rows_exported: int
    message: str
