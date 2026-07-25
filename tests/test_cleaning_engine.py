"""Tests for the cleaning pipeline."""

from __future__ import annotations

from playlistforge.cleaning.engine import CleaningEngine
from playlistforge.core.enums import CleaningRuleType
from playlistforge.core.models import CleaningRule, CleaningRules, Playlist, Video
from playlistforge.settings.defaults import default_cleaning_rules


def test_clean_title_applies_ordered_rules() -> None:
    rules = CleaningRules(
        rules=(
            CleaningRule("Remove LIVE", CleaningRuleType.LITERAL_REMOVE, pattern="LIVE"),
            CleaningRule("Collapse", CleaningRuleType.COLLAPSE_SPACES),
            CleaningRule("Trim", CleaningRuleType.TRIM_WHITESPACE),
        )
    )

    assert CleaningEngine().clean_title("  LIVE  Introduction   ", rules) == "Introduction"


def test_apply_playlist_preserves_original_title() -> None:
    video = Video(1, 1, "HD Introduction", "abc123XYZ00", "watch", "embed", "thumb")
    playlist = Playlist("PL1234567890", "Course", None, "url", None, (video,))
    rules = CleaningRules(
        rules=(CleaningRule("Remove HD", CleaningRuleType.LITERAL_REMOVE, pattern="HD"),)
    )

    cleaned = CleaningEngine().apply_playlist(playlist, rules)

    assert cleaned.videos[0].title == "HD Introduction"
    assert cleaned.videos[0].title_cleaned == " Introduction"


def test_default_rules_clean_empty_separators_and_brackets() -> None:
    title = (
        "CS201 Short Lecture - 03 | VU Short Lecture | "
        "Introduction to Programming in (Urdu / Hindi)"
    )

    cleaned = CleaningEngine().clean_title(title, default_cleaning_rules())

    assert cleaned == "CS201 Short Lecture - 03 | Introduction to Programming"
