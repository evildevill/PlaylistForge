"""Serialization helpers for settings models."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from playlistforge.core.enums import (
    CleaningRuleType,
    ClipboardFormat,
    ExportFormat,
    ExportMode,
    ThemeMode,
)
from playlistforge.core.models import (
    ApplicationSettings,
    CleaningPreset,
    CleaningRule,
    CleaningRules,
    ExportOptions,
)
from playlistforge.settings.defaults import default_settings

SETTINGS_VERSION = 1


def to_jsonable(value: object) -> object:
    """Convert dataclasses, enums, paths, and tuples into JSON-safe values."""
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value


JsonValue = object


def settings_to_payload(settings: ApplicationSettings) -> dict[str, JsonValue]:
    """Serialize settings with a schema version."""
    return {
        "version": SETTINGS_VERSION,
        "settings": to_jsonable(settings),
    }


def _cleaning_rule_from_payload(payload: dict[str, JsonValue]) -> CleaningRule:
    return CleaningRule(
        name=str(payload.get("name", "")),
        rule_type=CleaningRuleType(payload.get("rule_type", CleaningRuleType.LITERAL_REMOVE)),
        enabled=bool(payload.get("enabled", True)),
        pattern=str(payload.get("pattern", "")),
        replacement=str(payload.get("replacement", "")),
        case_sensitive=bool(payload.get("case_sensitive", False)),
    )


def _cleaning_rules_from_payload(payload: dict[str, JsonValue]) -> CleaningRules:
    rules = tuple(_cleaning_rule_from_payload(item) for item in payload.get("rules", []))
    return CleaningRules(rules=rules, active_preset=payload.get("active_preset"))


def _export_options_from_payload(payload: dict[str, JsonValue]) -> ExportOptions:
    directory = payload.get("destination_directory")
    return ExportOptions(
        format=ExportFormat(payload.get("format", ExportFormat.JSON)),
        fields=tuple(payload.get("fields", ExportOptions().fields)),
        mode=ExportMode(payload.get("mode", ExportMode.INDIVIDUAL)),
        clipboard_format=ClipboardFormat(
            payload.get("clipboard_format", ClipboardFormat.ALL_FIELDS)
        ),
        include_playlist_metadata=bool(payload.get("include_playlist_metadata", False)),
        use_cleaned_titles=bool(payload.get("use_cleaned_titles", True)),
        pretty_json=bool(payload.get("pretty_json", True)),
        destination_directory=Path(directory) if directory else None,
        filename=payload.get("filename"),
    )


def settings_from_payload(payload: dict[str, JsonValue]) -> ApplicationSettings:
    """Deserialize settings payload, tolerating missing keys."""
    defaults = default_settings()
    raw = payload.get("settings", payload)
    export_options = _export_options_from_payload(raw.get("export_options", {}))
    cleaning = _cleaning_rules_from_payload(raw.get("cleaning", {})) or defaults.cleaning
    export_dir = raw.get("last_export_directory")
    return ApplicationSettings(
        theme=ThemeMode(raw.get("theme", defaults.theme)),
        window_width=int(raw.get("window_width", defaults.window_width)),
        window_height=int(raw.get("window_height", defaults.window_height)),
        last_export_directory=Path(export_dir) if export_dir else None,
        recent_playlists=tuple(raw.get("recent_playlists", defaults.recent_playlists)),
        favorites=tuple(raw.get("favorites", defaults.favorites)),
        cleaning=cleaning,
        export_options=export_options,
        last_filename=str(raw.get("last_filename", defaults.last_filename)),
        visible_columns=tuple(raw.get("visible_columns", defaults.visible_columns)),
        column_widths={str(k): int(v) for k, v in raw.get("column_widths", {}).items()},
    )


__all__ = [
    "ApplicationSettings",
    "CleaningPreset",
    "SETTINGS_VERSION",
    "settings_from_payload",
    "settings_to_payload",
]
