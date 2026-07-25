"""Main PlaylistForge window."""

from __future__ import annotations

import logging
from dataclasses import replace

from playlistforge.cleaning.engine import CleaningEngine
from playlistforge.cleaning.history import CleaningHistory
from playlistforge.core.enums import ClipboardFormat, ExportFormat
from playlistforge.core.models import (
    ApplicationSettings,
    CleaningRules,
    ExportOptions,
    ExtractionProgress,
    ExtractionRequest,
    ExtractionResult,
    Playlist,
)
from playlistforge.export.clipboard import format_for_clipboard
from playlistforge.export.registry import default_exporter_registry
from playlistforge.extraction.service import ExtractionService
from playlistforge.extraction.url_validator import extract_urls_from_text
from playlistforge.history.repository import add_recent_playlist
from playlistforge.settings.repository import SettingsRepository
from playlistforge.ui.dialogs.error_dialog import show_error
from playlistforge.ui.dialogs.export_dialog import choose_export_path
from playlistforge.ui.dialogs.settings_dialog import SettingsDialog
from playlistforge.ui.models.proxy_models import VideoFilterProxyModel
from playlistforge.ui.models.video_table_model import VideoTableModel
from playlistforge.ui.theme import app_stylesheet, apply_theme
from playlistforge.ui.widgets.cleaning_panel import CleaningPanel
from playlistforge.ui.widgets.export_panel import ExportPanel
from playlistforge.ui.widgets.history_panel import HistoryPanel
from playlistforge.ui.widgets.playlist_summary import PlaylistSummary
from playlistforge.ui.widgets.status_panel import StatusPanel
from playlistforge.ui.widgets.url_input_panel import UrlInputPanel
from playlistforge.ui.widgets.video_table import VideoTable

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QSplitter,
        QTabWidget,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    QApplication = object  # type: ignore[assignment]
    QCloseEvent = object  # type: ignore[assignment]
    QMainWindow = object  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


def create_application(argv: list[str], settings: ApplicationSettings) -> QApplication:
    """Create and configure the Qt application."""
    app = QApplication(argv)
    app.setApplicationName("PlaylistForge")
    app.setOrganizationName("PlaylistForge")
    apply_theme(app, settings.theme)
    app.setStyleSheet(app_stylesheet())
    return app


def create_main_window(
    settings_repository: SettingsRepository,
    settings: ApplicationSettings,
) -> MainWindow:
    """Factory used by the bootstrap module."""
    return MainWindow(settings_repository, settings)


class MainWindow(QMainWindow):
    """Main desktop application window."""

    def __init__(
        self,
        settings_repository: SettingsRepository,
        settings: ApplicationSettings,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._settings = settings
        self._playlists: tuple[Playlist, ...] = ()
        self._cleaning_engine = CleaningEngine()
        self._cleaning_history = CleaningHistory()
        self._exporters = default_exporter_registry()
        self._extraction = ExtractionService()

        self.setWindowTitle("PlaylistForge")
        self.resize(settings.window_width, settings.window_height)
        self._build_ui()
        self._connect()
        self._refresh_settings_panels()

    def _build_ui(self) -> None:
        self.url_panel = UrlInputPanel()
        self.history_panel = HistoryPanel()
        self.summary = PlaylistSummary()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search videos...")
        self.video_model = VideoTableModel()
        self.video_proxy = VideoFilterProxyModel()
        self.video_proxy.setSourceModel(self.video_model)
        self.video_table = VideoTable()
        self.video_table.setModel(self.video_proxy)
        self.export_panel = ExportPanel()
        self.cleaning_panel = CleaningPanel(self._settings.cleaning)
        self.status_panel = StatusPanel()

        self.tabs = QTabWidget()
        merged_tab = QWidget()
        merged_layout = QVBoxLayout(merged_tab)
        merged_layout.addWidget(self.summary)
        merged_layout.addWidget(self.search_input)
        merged_layout.addWidget(self.video_table)
        self.tabs.addTab(merged_tab, "Merged Preview")

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self.url_panel)
        left_layout.addWidget(self.history_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(self.cleaning_panel)
        right_layout.addWidget(self.export_panel)
        right_layout.addStretch(1)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(QLabel("Extract • Clean • Transform • Export"))
        center_layout.addWidget(self.tabs)
        center_layout.addWidget(self.status_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 1)
        self.setCentralWidget(splitter)
        self._build_toolbar()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        settings_action = QAction("Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._open_settings)
        export_action = QAction("Export", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(
            lambda: self._export_file(str(self.export_panel.format_combo.currentData()))
        )
        toolbar.addAction(settings_action)
        toolbar.addAction(export_action)

    def _connect(self) -> None:
        self.url_panel.extract_requested.connect(self._extract)
        self.url_panel.paste_requested.connect(self._paste)
        self.url_panel.cancel_requested.connect(self._extraction.cancel)
        self.history_panel.url_selected.connect(self._load_url_from_history)
        self.search_input.textChanged.connect(self.video_proxy.setFilterFixedString)
        self.cleaning_panel.apply_requested.connect(self._apply_cleaning)
        self.cleaning_panel.undo_requested.connect(self._undo_cleaning)
        self.cleaning_panel.reset_requested.connect(self._reset_cleaning)
        self.export_panel.export_requested.connect(self._export_file)
        self.export_panel.copy_requested.connect(self._copy_export)
        self._extraction.progress.connect(self._on_progress)
        self._extraction.finished.connect(self._on_extraction_finished)
        self._extraction.failed.connect(self._on_extraction_failed)
        self._extraction.cancelled.connect(self._on_extraction_cancelled)

    def _paste(self) -> None:
        text = QApplication.clipboard().text()
        self.url_panel.url_input.setPlainText(text)

    def _extract(self, text: str) -> None:
        urls = extract_urls_from_text(text)
        if not urls:
            QMessageBox.warning(
                self,
                "PlaylistForge",
                "Paste at least one valid YouTube playlist URL.",
            )
            return
        self.url_panel.set_busy(True)
        self.status_panel.set_status("Starting extraction...", 0)
        self._extraction.start(ExtractionRequest(urls=urls))

    def _on_progress(self, progress: ExtractionProgress) -> None:
        self.status_panel.set_status(progress.message, progress.percent)

    def _on_extraction_finished(self, result: ExtractionResult) -> None:
        self.url_panel.set_busy(False)
        self._playlists = result.playlists
        self._update_playlist_views()
        for playlist in result.playlists:
            self._settings = add_recent_playlist(self._settings, playlist.webpage_url)
        self._save_settings()
        self.status_panel.set_status(f"Loaded {len(result.playlists)} playlist(s).", 100)

    def _on_extraction_failed(self, error: BaseException) -> None:
        self.url_panel.set_busy(False)
        self.status_panel.set_status("Extraction failed.", 0)
        show_error(self, error)

    def _on_extraction_cancelled(self) -> None:
        self.url_panel.set_busy(False)
        self.status_panel.set_status("Extraction cancelled.", 0)

    def _update_playlist_views(self) -> None:
        self.video_model.set_playlists(self._playlists)
        self.summary.set_playlist(self._playlists[0] if self._playlists else None)
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        for playlist in self._playlists:
            label = QLabel(
                f"{playlist.title}\n{playlist.channel or 'Unknown channel'}\n"
                f"{playlist.video_count} videos\n{playlist.playlist_id}"
            )
            label.setMargin(18)
            self.tabs.addTab(label, playlist.title[:28] or "Playlist")
        self._refresh_settings_panels()

    def _active_cleaning_rules(self) -> CleaningRules:
        enabled = set(self.cleaning_panel.enabled_rule_indexes())
        rules = tuple(
            replace(rule, enabled=index in enabled)
            for index, rule in enumerate(self._settings.cleaning.rules)
        )
        return replace(self._settings.cleaning, rules=rules)

    def _apply_cleaning(self) -> None:
        if not self._playlists:
            return
        self._cleaning_history.push(self._playlists[0])
        rules = self._active_cleaning_rules()
        self._playlists = tuple(
            self._cleaning_engine.apply_playlist(playlist, rules)
            for playlist in self._playlists
        )
        self._settings = replace(self._settings, cleaning=rules)
        self._update_playlist_views()
        self._save_settings()

    def _undo_cleaning(self) -> None:
        previous = self._cleaning_history.pop()
        if previous is None:
            return
        self._playlists = (previous, *self._playlists[1:])
        self._update_playlist_views()

    def _reset_cleaning(self) -> None:
        self._playlists = tuple(
            self._cleaning_engine.reset_playlist(playlist) for playlist in self._playlists
        )
        self._update_playlist_views()

    def _export_options(self, export_format: str) -> ExportOptions:
        return replace(
            self._settings.export_options,
            format=ExportFormat(export_format),
            pretty_json=self.export_panel.pretty_json.isChecked(),
            use_cleaned_titles=self.export_panel.cleaned_titles.isChecked(),
            destination_directory=self._settings.last_export_directory,
            filename=self._settings.last_filename,
        )

    def _export_file(self, export_format: str) -> None:
        if not self._playlists:
            QMessageBox.information(self, "PlaylistForge", "Extract a playlist before exporting.")
            return
        options = self._export_options(export_format)
        exporter = self._exporters.get(options.format)
        destination = choose_export_path(
            self,
            exporter.file_extension,
            self._settings.last_export_directory,
        )
        if destination is None:
            return
        try:
            result = exporter.export(self._playlists, options, destination)
        except Exception as exc:
            LOGGER.exception("Export failed")
            show_error(self, exc)
            return
        self._settings = replace(
            self._settings,
            last_export_directory=result.destination.parent if result.destination else None,
            last_filename=(
                result.destination.stem if result.destination else self._settings.last_filename
            ),
            export_options=options,
        )
        self._save_settings()
        self.status_panel.set_status(result.message, 100)

    def _copy_export(self) -> None:
        if not self._playlists:
            return
        options = replace(
            self._export_options(ExportFormat.CLIPBOARD.value),
            clipboard_format=ClipboardFormat.ALL_FIELDS,
        )
        QApplication.clipboard().setText(format_for_clipboard(self._playlists, options))
        self.status_panel.set_status("Copied playlist data to clipboard.", 100)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._settings)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        self._settings = replace(self._settings, theme=dialog.selected_theme())
        apply_theme(QApplication.instance(), self._settings.theme)
        self._save_settings()

    def _load_url_from_history(self, url: str) -> None:
        self.url_panel.url_input.setPlainText(url)

    def _refresh_settings_panels(self) -> None:
        self.history_panel.set_recent(self._settings.recent_playlists)
        self.history_panel.set_favorites(self._settings.favorites)

    def _save_settings(self) -> None:
        try:
            self._settings_repository.save(self._settings)
        except Exception:
            LOGGER.exception("Failed to save settings")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._settings = replace(
            self._settings,
            window_width=self.width(),
            window_height=self.height(),
        )
        self._save_settings()
        super().closeEvent(event)
