"""Rule implementations for title cleaning."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from playlistforge.core.enums import CleaningRuleType
from playlistforge.core.models import CleaningRule


class CompiledCleaningRule(ABC):
    """Executable cleaning rule."""

    def __init__(self, definition: CleaningRule) -> None:
        self.definition = definition

    @abstractmethod
    def apply(self, title: str) -> str:
        """Return a transformed title."""


class LiteralRemoveRule(CompiledCleaningRule):
    """Remove a literal phrase."""

    def apply(self, title: str) -> str:
        flags = 0 if self.definition.case_sensitive else re.IGNORECASE
        return re.sub(re.escape(self.definition.pattern), "", title, flags=flags)


class RegexReplaceRule(CompiledCleaningRule):
    """Apply a user-defined regex replacement."""

    def apply(self, title: str) -> str:
        flags = 0 if self.definition.case_sensitive else re.IGNORECASE
        return re.sub(self.definition.pattern, self.definition.replacement, title, flags=flags)


class CollapseSpacesRule(CompiledCleaningRule):
    """Collapse repeated whitespace into single spaces."""

    def apply(self, title: str) -> str:
        return re.sub(r"\s+", " ", title)


class TrimWhitespaceRule(CompiledCleaningRule):
    """Trim leading and trailing whitespace."""

    def apply(self, title: str) -> str:
        return title.strip()


class RemoveYearRule(CompiledCleaningRule):
    """Remove a year-like literal."""

    def apply(self, title: str) -> str:
        return re.sub(r"\b(2024|2025|2026)\b", "", title)


def compile_rule(definition: CleaningRule) -> CompiledCleaningRule:
    """Compile a serializable rule definition into an executable rule."""
    match definition.rule_type:
        case CleaningRuleType.LITERAL_REMOVE:
            return LiteralRemoveRule(definition)
        case CleaningRuleType.REGEX_REPLACE:
            return RegexReplaceRule(definition)
        case CleaningRuleType.COLLAPSE_SPACES:
            return CollapseSpacesRule(definition)
        case CleaningRuleType.TRIM_WHITESPACE:
            return TrimWhitespaceRule(definition)
        case CleaningRuleType.REMOVE_YEAR:
            return RemoveYearRule(definition)
