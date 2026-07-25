"""Settings dialog."""

from __future__ import annotations

from playlistforge.core.enums import ThemeMode
from playlistforge.core.models import ApplicationSettings

try:
    from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore[assignment, misc]


class SettingsDialog(QDialog):
    """Small settings dialog for theme selection."""

    def __init__(self, settings: ApplicationSettings) -> None:
        super().__init__()
        self.setWindowTitle("Settings")
        self.theme_combo = QComboBox()
        for theme in ThemeMode:
            self.theme_combo.addItem(theme.value.title(), theme.value)
        self.theme_combo.setCurrentText(settings.theme.value.title())
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Theme", self.theme_combo)
        layout.addWidget(buttons)

    def selected_theme(self) -> ThemeMode:
        """Return selected theme."""
        return ThemeMode(str(self.theme_combo.currentData()))
