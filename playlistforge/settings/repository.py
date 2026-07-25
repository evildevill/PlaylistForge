"""Settings repository backed by a JSON file."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from playlistforge.core.models import ApplicationSettings
from playlistforge.settings.defaults import default_settings
from playlistforge.settings.models import settings_from_payload, settings_to_payload

LOGGER = logging.getLogger(__name__)
APP_DIR_NAME = "PlaylistForge"


def user_config_dir() -> Path:
    """Return the platform-appropriate config directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_DIR_NAME


class SettingsRepository:
    """Load and save user settings."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or user_config_dir() / "settings.json"

    def load(self) -> ApplicationSettings:
        """Load settings, falling back to defaults on corruption or absence."""
        if not self.path.exists():
            return default_settings()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return settings_from_payload(payload)
        except Exception:
            LOGGER.exception("Failed to load settings from %s", self.path)
            return default_settings()

    def save(self, settings: ApplicationSettings) -> None:
        """Persist settings atomically enough for a desktop utility."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        payload = settings_to_payload(settings)
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)

    def reset(self) -> ApplicationSettings:
        """Reset settings to defaults and persist them."""
        settings = default_settings()
        self.save(settings)
        return settings
