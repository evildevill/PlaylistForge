"""Cleaning controls."""

from __future__ import annotations

from playlistforge.core.models import CleaningRules

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QCheckBox,
        QGroupBox,
        QPushButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    Signal = object  # type: ignore[assignment]
    QGroupBox = object  # type: ignore[assignment]


class CleaningPanel(QGroupBox):
    """Panel for enabling rules and applying title cleaning."""

    apply_requested = Signal()
    reset_requested = Signal()
    undo_requested = Signal()

    def __init__(self, rules: CleaningRules) -> None:
        super().__init__("Clean Titles")
        self._checkboxes: list[QCheckBox] = []
        rule_container = QWidget()
        rule_layout = QVBoxLayout(rule_container)
        for rule in rules.rules:
            checkbox = QCheckBox(rule.name)
            checkbox.setChecked(rule.enabled)
            self._checkboxes.append(checkbox)
            rule_layout.addWidget(checkbox)
        rule_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(rule_container)
        scroll.setMinimumHeight(180)

        self.apply_button = QPushButton("Apply")
        self.undo_button = QPushButton("Undo")
        self.reset_button = QPushButton("Reset")

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.reset_button)

        self.apply_button.clicked.connect(self.apply_requested.emit)
        self.undo_button.clicked.connect(self.undo_requested.emit)
        self.reset_button.clicked.connect(self.reset_requested.emit)

    def enabled_rule_indexes(self) -> tuple[int, ...]:
        """Return indexes for enabled rules."""
        return tuple(
            index for index, checkbox in enumerate(self._checkboxes) if checkbox.isChecked()
        )
