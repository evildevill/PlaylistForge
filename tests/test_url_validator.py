"""Tests for playlist URL validation."""

from __future__ import annotations

from playlistforge.core.enums import UrlType
from playlistforge.extraction.url_validator import (
    classify_url,
    extract_urls_from_text,
    normalize_playlist_url,
)


def test_normalize_playlist_url() -> None:
    url = "https://www.youtube.com/watch?v=x&list=PL1234567890ABC"

    assert normalize_playlist_url(url) == "https://www.youtube.com/playlist?list=PL1234567890ABC"


def test_extract_urls_deduplicates() -> None:
    text = (
        "https://www.youtube.com/playlist?list=PL1234567890ABC "
        "https://www.youtube.com/watch?v=x&list=PL1234567890ABC"
    )

    assert extract_urls_from_text(text) == ("https://www.youtube.com/playlist?list=PL1234567890ABC",)


def test_classify_playlist_url() -> None:
    assert classify_url("https://www.youtube.com/playlist?list=PL1234567890ABC") == UrlType.PLAYLIST
