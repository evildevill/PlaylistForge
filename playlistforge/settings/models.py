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
from playlistforge.settings.defaults import default_cleaning_rules, default_settings

SETTINGS_VERSION = 1


def to_jsonable(value: object) -> object:
    """Convert dataclasses, enums, paths, and tuples into JSON-safe values."""
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}  # type: ignore[arg-type]
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


def _mapping(value: object) -> dict[str, object]:
    """Return a string-keyed mapping when possible."""
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def _string(value: object, default: str = "") -> str:
    """Return value when it is a string, otherwise a fallback."""
    return value if isinstance(value, str) else default


def _optional_string(value: object) -> str | None:
    """Return a string value or None."""
    return value if isinstance(value, str) else None


def _string_tuple(value: object, default: tuple[str, ...]) -> tuple[str, ...]:
    """Return a tuple of strings from list-like persisted values."""
    if not isinstance(value, list | tuple):
        return default
    return tuple(str(item) for item in value)


def _integer(value: object, default: int) -> int:
    """Return an integer from simple persisted scalar values."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return default


def settings_to_payload(settings: ApplicationSettings) -> dict[str, object]:
    """Serialize settings with a schema version."""
    settings_payload = to_jsonable(settings)
    return {
        "version": SETTINGS_VERSION,
        "settings": settings_payload,
    }


def _cleaning_rule_from_payload(payload: dict[str, object]) -> CleaningRule:
    rule_type = _string(payload.get("rule_type"), CleaningRuleType.LITERAL_REMOVE.value)
    return CleaningRule(
        name=_string(payload.get("name")),
        rule_type=CleaningRuleType(rule_type),
        enabled=bool(payload.get("enabled", True)),
        pattern=str(payload.get("pattern", "")),
        replacement=str(payload.get("replacement", "")),
        case_sensitive=bool(payload.get("case_sensitive", False)),
    )


def _cleaning_rules_from_payload(payload: dict[str, object]) -> CleaningRules:
    rules_value = payload.get("rules", [])
    loaded_rules = (
        tuple(_cleaning_rule_from_payload(_mapping(item)) for item in rules_value)
        if isinstance(rules_value, list | tuple)
        else ()
    )
    default_rules = default_cleaning_rules().rules
    existing_types = {rule.rule_type for rule in loaded_rules}
    missing_default_rules = tuple(
        rule for rule in default_rules if rule.rule_type not in existing_types
    )
    rules = (*loaded_rules, *missing_default_rules)
    return CleaningRules(rules=rules, active_preset=_optional_string(payload.get("active_preset")))


def _export_options_from_payload(payload: dict[str, object]) -> ExportOptions:
    directory = payload.get("destination_directory")
    filename = _optional_string(payload.get("filename"))
    export_format = _string(payload.get("format"), ExportFormat.JSON.value)
    export_mode = _string(payload.get("mode"), ExportMode.INDIVIDUAL.value)
    clipboard_format = _string(
        payload.get("clipboard_format"),
        ClipboardFormat.ALL_FIELDS.value,
    )
    return ExportOptions(
        format=ExportFormat(export_format),
        fields=_string_tuple(payload.get("fields"), ExportOptions().fields),
        mode=ExportMode(export_mode),
        clipboard_format=ClipboardFormat(clipboard_format),
        include_playlist_metadata=bool(payload.get("include_playlist_metadata", False)),
        use_cleaned_titles=bool(payload.get("use_cleaned_titles", True)),
        pretty_json=bool(payload.get("pretty_json", True)),
        destination_directory=Path(directory) if isinstance(directory, str) else None,
        filename=filename,
    )


def settings_from_payload(payload: dict[str, object]) -> ApplicationSettings:
    """Deserialize settings payload, tolerating missing keys."""
    defaults = default_settings()
    raw = _mapping(payload.get("settings", payload))
    export_options = _export_options_from_payload(_mapping(raw.get("export_options", {})))
    cleaning = _cleaning_rules_from_payload(_mapping(raw.get("cleaning", {}))) or defaults.cleaning
    export_dir = raw.get("last_export_directory")
    column_widths = _mapping(raw.get("column_widths", {}))
    return ApplicationSettings(
        theme=ThemeMode(_string(raw.get("theme"), defaults.theme.value)),
        window_width=_integer(raw.get("window_width"), defaults.window_width),
        window_height=_integer(raw.get("window_height"), defaults.window_height),
        last_export_directory=Path(export_dir) if isinstance(export_dir, str) else None,
        recent_playlists=_string_tuple(
            raw.get("recent_playlists"),
            defaults.recent_playlists,
        ),
        favorites=_string_tuple(raw.get("favorites"), defaults.favorites),
        cleaning=cleaning,
        export_options=export_options,
        last_filename=str(raw.get("last_filename", defaults.last_filename)),
        visible_columns=_string_tuple(raw.get("visible_columns"), defaults.visible_columns),
        column_widths={
            str(column): _integer(width, 120) for column, width in column_widths.items()
        },
    )


__all__ = [
    "ApplicationSettings",
    "CleaningPreset",
    "SETTINGS_VERSION",
    "settings_from_payload",
    "settings_to_payload",
]
