"""Application theming."""

from __future__ import annotations

from playlistforge.core.enums import ThemeMode

try:
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover
    QApplication = object  # type: ignore[assignment, misc]
    QColor = object  # type: ignore[assignment, misc]
    QPalette = object  # type: ignore[assignment, misc]


def apply_theme(app: QApplication, theme: ThemeMode) -> None:
    """Apply a light, dark, or system theme."""
    app.setStyle("Fusion")
    if theme == ThemeMode.SYSTEM:
        app.setPalette(app.style().standardPalette())
        return
    palette = QPalette()
    if theme == ThemeMode.DARK:
        palette.setColor(QPalette.ColorRole.Window, QColor(31, 34, 40))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(238, 241, 245))
        palette.setColor(QPalette.ColorRole.Base, QColor(23, 25, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(39, 43, 51))
        palette.setColor(QPalette.ColorRole.Text, QColor(238, 241, 245))
        palette.setColor(QPalette.ColorRole.Button, QColor(43, 48, 57))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(238, 241, 245))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 121, 247))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    else:
        palette.setColor(QPalette.ColorRole.Window, QColor(248, 249, 251))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 34, 39))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(243, 245, 248))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 34, 39))
        palette.setColor(QPalette.ColorRole.Button, QColor(246, 247, 249))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 34, 39))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(35, 106, 232))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)


def app_stylesheet() -> str:
    """Return the app stylesheet."""
    return """
    QWidget {
        font-size: 13px;
    }
    QMainWindow {
        background: palette(window);
    }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
        border: 1px solid rgba(127, 127, 127, 80);
        border-radius: 6px;
        padding: 8px;
        background: palette(base);
    }
    QPushButton {
        border: 1px solid rgba(127, 127, 127, 75);
        border-radius: 6px;
        padding: 8px 12px;
        background: palette(button);
    }
    QPushButton:pressed {
        background: palette(alternate-base);
    }
    QTableView {
        gridline-color: rgba(127, 127, 127, 50);
        selection-background-color: palette(highlight);
        selection-color: palette(highlighted-text);
        alternate-background-color: palette(alternate-base);
    }
    QHeaderView::section {
        padding: 7px;
        border: 0;
        border-bottom: 1px solid rgba(127, 127, 127, 80);
        background: palette(alternate-base);
        font-weight: 600;
    }
    QGroupBox {
        font-weight: 600;
        border: 1px solid rgba(127, 127, 127, 60);
        border-radius: 8px;
        margin-top: 12px;
        padding: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
    }
    """
