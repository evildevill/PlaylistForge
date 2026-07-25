"""Application bootstrap for PlaylistForge."""

from __future__ import annotations

import sys

from playlistforge.logging.setup import configure_logging
from playlistforge.settings.repository import SettingsRepository
from playlistforge.ui.main_window import create_application, create_main_window


def main() -> int:
    """Start the PlaylistForge Qt application."""
    configure_logging()
    settings_repository = SettingsRepository()
    settings = settings_repository.load()
    app = create_application(sys.argv, settings)
    window = create_main_window(settings_repository, settings)
    window.show()
    return app.exec()
