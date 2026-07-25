"""Default settings and rules."""

from __future__ import annotations

from playlistforge.core.enums import CleaningRuleType
from playlistforge.core.models import ApplicationSettings, CleaningRule, CleaningRules


def default_cleaning_rules() -> CleaningRules:
    """Return sensible starter cleaning rules."""
    removals = (
        "VU Short Lecture",
        "Urdu / Hindi",
        "LIVE",
        "Official",
        "HD",
        "2024",
        "2025",
        "2026",
    )
    rules = tuple(
        CleaningRule(
            name=f"Remove {text}",
            rule_type=CleaningRuleType.LITERAL_REMOVE,
            pattern=text,
        )
        for text in removals
    )
    rules += (
        CleaningRule(
            name="Collapse multiple spaces",
            rule_type=CleaningRuleType.COLLAPSE_SPACES,
            pattern=r"\s+",
            replacement=" ",
        ),
        CleaningRule(
            name="Clean empty brackets and separators",
            rule_type=CleaningRuleType.CLEAN_PUNCTUATION,
        ),
        CleaningRule(
            name="Trim whitespace",
            rule_type=CleaningRuleType.TRIM_WHITESPACE,
        ),
    )
    return CleaningRules(rules=rules, active_preset="Default")


def default_settings() -> ApplicationSettings:
    """Return application defaults."""
    return ApplicationSettings(cleaning=default_cleaning_rules())
