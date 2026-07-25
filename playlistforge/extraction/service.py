"""Extraction service facade used by the GUI."""

from __future__ import annotations

from playlistforge.core.models import ExtractionRequest
from playlistforge.extraction.worker import ExtractionWorker

try:
    from PySide6.QtCore import QObject, QThread, Signal
except ImportError:  # pragma: no cover
    QObject = object  # type: ignore[assignment]
    QThread = None  # type: ignore[assignment]

    class Signal:  # type: ignore[no-redef]
        def __init__(self, *args: object) -> None:
            pass

        def emit(self, *args: object) -> None:
            return None


class ExtractionService(QObject):
    """Coordinate extraction workers and expose UI-friendly signals."""

    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._thread = None
        self._worker: ExtractionWorker | None = None

    def start(self, request: ExtractionRequest) -> None:
        """Start a background extraction request."""
        if QThread is None:
            raise RuntimeError("PySide6 is required for threaded extraction.")
        if self._thread is not None:
            self.cancel()
        self._thread = QThread()
        self._worker = ExtractionWorker(request)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self.finished.emit)
        self._worker.failed.connect(self.failed.emit)
        self._worker.cancelled.connect(self.cancelled.emit)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._clear)
        self._thread.start()

    def cancel(self) -> None:
        """Cancel the active extraction if any."""
        if self._worker is not None:
            self._worker.cancel()

    def _clear(self) -> None:
        self._thread = None
        self._worker = None
