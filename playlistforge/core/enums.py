"""Shared enumerations used across PlaylistForge."""

from __future__ import annotations

from enum import StrEnum


class ThemeMode(StrEnum):
    """Supported application theme modes."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class ExportFormat(StrEnum):
    """Supported export targets."""

    JSON = "json"
    TXT = "txt"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    EXCEL = "excel"
    CLIPBOARD = "clipboard"


class ExportMode(StrEnum):
    """How multiple playlists should be exported."""

    INDIVIDUAL = "individual"
    MERGED = "merged"


class ClipboardFormat(StrEnum):
    """Clipboard-specific export variants."""

    ALL_FIELDS = "all_fields"
    URLS_ONLY = "urls_only"
    EMBED_URLS_ONLY = "embed_urls_only"
    IDS_ONLY = "ids_only"
    TITLES_ONLY = "titles_only"


class VideoAvailability(StrEnum):
    """Known availability state for a video."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PRIVATE = "private"
    DELETED = "deleted"
    UNKNOWN = "unknown"


class ExtractionStatus(StrEnum):
    """Lifecycle status for extraction requests."""

    QUEUED = "queued"
    RUNNING = "running"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


class CleaningRuleType(StrEnum):
    """Supported cleaning rule implementations."""

    LITERAL_REMOVE = "literal_remove"
    REGEX_REPLACE = "regex_replace"
    COLLAPSE_SPACES = "collapse_spaces"
    CLEAN_PUNCTUATION = "clean_punctuation"
    TRIM_WHITESPACE = "trim_whitespace"
    REMOVE_YEAR = "remove_year"


class UrlType(StrEnum):
    """Classification result for user-supplied URLs."""

    PLAYLIST = "playlist"
    VIDEO = "video"
    TEXT_FILE = "text_file"
    UNKNOWN = "unknown"
