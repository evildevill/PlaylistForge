"""Cleaning preset repository helpers."""

from __future__ import annotations

from playlistforge.core.models import CleaningPreset, CleaningRules


def preset_from_rules(name: str, rules: CleaningRules) -> CleaningPreset:
    """Create a named preset from active rules."""
    return CleaningPreset(name=name, rules=rules.rules)
