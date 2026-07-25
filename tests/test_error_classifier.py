"""Tests for extraction error classification."""

from __future__ import annotations

from playlistforge.core.errors import NetworkError, PrivatePlaylistError, RateLimitedError
from playlistforge.extraction.error_classifier import classify_extraction_error


def test_rate_limit_classification() -> None:
    assert isinstance(classify_extraction_error(RuntimeError("HTTP Error 429")), RateLimitedError)


def test_private_classification() -> None:
    error = classify_extraction_error(RuntimeError("private playlist"))

    assert isinstance(error, PrivatePlaylistError)


def test_network_classification() -> None:
    assert isinstance(classify_extraction_error(RuntimeError("connection reset")), NetworkError)
