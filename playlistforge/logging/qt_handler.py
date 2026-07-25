"""Qt-compatible logging hook used by future log viewers."""

from __future__ import annotations

import logging
from collections.abc import Callable


class QtLogHandler(logging.Handler):
    """A lightweight handler that forwards formatted log messages to a callback."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a formatted log record."""
        self._callback(self.format(record))
