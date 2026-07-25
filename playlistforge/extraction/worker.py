"""Qt worker objects for background extraction."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

from playlistforge.core.enums import ExtractionStatus
from playlistforge.core.errors import ExtractionCancelled, PlaylistForgeError
from playlistforge.core.models import ExtractionProgress, ExtractionRequest, ExtractionResult
from playlistforge.extraction.yt_dlp_client import YtDlpClient

LOGGER = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., object])

try:
    from PySide6.QtCore import QObject, Signal, Slot
except ImportError:  # pragma: no cover - allows non-GUI tests without PySide6 installed
    class QObject:  # type: ignore[no-redef]
        """Fallback QObject for environments without PySide6."""

    class Signal:  # type: ignore[no-redef]
        """Fallback signal placeholder."""

        def __init__(self, *args: object) -> None:
            self._callbacks: list[object] = []

        def emit(self, *args: object) -> None:
            return None

    def Slot(*args: object, **kwargs: object) -> Callable[[F], F]:  # type: ignore[no-redef]
        def decorator(func: F) -> F:
            return func

        return decorator


class ExtractionWorker(QObject):
    """Worker that extracts playlists away from the GUI thread."""

    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal()

    def __init__(self, request: ExtractionRequest) -> None:
        super().__init__()
        self._request = request
        self._cancel_requested = False

    @Slot()
    def run(self) -> None:
        """Run the extraction request."""
        playlists = []
        warnings: list[str] = []
        total = len(self._request.urls)
        client = YtDlpClient(progress_callback=self.progress.emit)
        try:
            for index, url in enumerate(self._request.urls, start=1):
                if self._cancel_requested:
                    raise ExtractionCancelled()
                self.progress.emit(
                    ExtractionProgress(
                        status=ExtractionStatus.RUNNING,
                        message=f"Extracting playlist {index} of {total}",
                        current=index - 1,
                        total=total,
                        url=url,
                    )
                )
                playlist = client.extract_playlist(
                    url,
                    cancel_requested=self.cancel_requested,
                    retry_count=self._request.retry_count,
                    timeout_seconds=self._request.timeout_seconds,
                )
                playlists.append(playlist)
                self.progress.emit(
                    ExtractionProgress(
                        status=ExtractionStatus.RUNNING,
                        message=f"Loaded {playlist.video_count} videos",
                        current=index,
                        total=total,
                        url=url,
                    )
                )
            self.finished.emit(
                ExtractionResult(playlists=tuple(playlists), warnings=tuple(warnings))
            )
        except ExtractionCancelled:
            self.cancelled.emit()
        except PlaylistForgeError as exc:
            LOGGER.exception("Extraction failed")
            self.failed.emit(exc)
        except Exception as exc:
            LOGGER.exception("Unexpected extraction failure")
            from playlistforge.extraction.error_classifier import classify_extraction_error

            self.failed.emit(classify_extraction_error(exc))

    @Slot()
    def cancel(self) -> None:
        """Request cancellation."""
        self._cancel_requested = True

    def cancel_requested(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._cancel_requested
