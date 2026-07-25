"""Logging setup for PlaylistForge."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_DIR_NAME = "PlaylistForge"
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def user_log_dir() -> Path:
    """Return the platform-appropriate log directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Logs"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / APP_DIR_NAME / "logs"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure rotating file and console logging."""
    log_dir = user_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT)
    app_handler = RotatingFileHandler(
        log_dir / "playlistforge.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(level)

    error_handler = RotatingFileHandler(
        log_dir / "playlistforge.error.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    root.addHandler(app_handler)
    root.addHandler(error_handler)
    root.addHandler(console_handler)
