"""Thin, isolated wrapper around yt-dlp."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from playlistforge.core.errors import ExtractionCancelled, ExtractionError
from playlistforge.core.models import ExtractionProgress, Playlist
from playlistforge.extraction.error_classifier import classify_extraction_error
from playlistforge.extraction.parser import parse_playlist

LOGGER = logging.getLogger(__name__)
CancelCallback = Callable[[], bool]
ProgressCallback = Callable[[ExtractionProgress], None]


class YtDlpLogger:
    """Bridge yt-dlp logger callbacks into Python logging."""

    def debug(self, message: str) -> None:
        """Log debug/info messages from yt-dlp."""
        LOGGER.debug(message)

    def info(self, message: str) -> None:
        """Log informational messages from yt-dlp."""
        LOGGER.info(message)

    def warning(self, message: str) -> None:
        """Log warnings from yt-dlp."""
        LOGGER.warning(message)

    def error(self, message: str) -> None:
        """Log errors from yt-dlp."""
        LOGGER.error(message)


class YtDlpClient:
    """Extract playlists through the yt-dlp Python API."""

    def __init__(self, *, progress_callback: ProgressCallback | None = None) -> None:
        self._progress_callback = progress_callback

    def extract_playlist(
        self,
        url: str,
        *,
        cancel_requested: CancelCallback | None = None,
        retry_count: int = 2,
        timeout_seconds: int = 30,
    ) -> Playlist:
        """Extract a playlist, retrying expected transient failures."""
        try:
            import yt_dlp
        except ImportError as exc:
            raise ExtractionError("yt-dlp is not installed.", details=str(exc)) from exc

        last_error: BaseException | None = None
        for attempt in range(retry_count + 1):
            if cancel_requested and cancel_requested():
                raise ExtractionCancelled()
            try:
                started = time.monotonic()
                options = self._options(cancel_requested, timeout_seconds)
                with yt_dlp.YoutubeDL(options) as ydl:
                    LOGGER.info("Starting extraction for %s", url)
                    info = ydl.extract_info(url, download=False)
                    sanitized = ydl.sanitize_info(info)
                duration = time.monotonic() - started
                playlist = parse_playlist(sanitized, duration_seconds=duration)
                LOGGER.info(
                    "Extracted playlist %s with %s videos in %.2fs",
                    playlist.playlist_id,
                    playlist.video_count,
                    duration,
                )
                return playlist
            except ExtractionCancelled:
                LOGGER.info("Extraction cancelled for %s", url)
                raise
            except Exception as exc:
                last_error = exc
                classified = classify_extraction_error(exc)
                LOGGER.warning(
                    "Extraction attempt %s/%s failed for %s: %s",
                    attempt + 1,
                    retry_count + 1,
                    url,
                    classified.user_message,
                )
                if attempt >= retry_count:
                    raise classified from exc
                time.sleep(min(2**attempt, 5))
        raise classify_extraction_error(last_error or RuntimeError("Unknown extraction failure"))

    def _options(
        self,
        cancel_requested: CancelCallback | None,
        timeout_seconds: int,
    ) -> dict[str, object]:
        def hook(payload: dict[str, object]) -> None:
            if cancel_requested and cancel_requested():
                raise ExtractionCancelled()
            status = str(payload.get("status", "running"))
            if self._progress_callback:
                from playlistforge.core.enums import ExtractionStatus

                self._progress_callback(
                    ExtractionProgress(
                        status=ExtractionStatus.RUNNING,
                        message=f"yt-dlp: {status}",
                    )
                )

        return {
            "extract_flat": False,
            "ignoreerrors": True,
            "logger": YtDlpLogger(),
            "noplaylist": False,
            "playlistend": None,
            "progress_hooks": [hook],
            "quiet": True,
            "retries": 3,
            "skip_download": True,
            "socket_timeout": timeout_seconds,
            "yes_playlist": True,
        }
