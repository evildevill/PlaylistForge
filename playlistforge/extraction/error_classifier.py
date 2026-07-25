"""Translate lower-level extraction failures into application errors."""

from __future__ import annotations

from playlistforge.core.errors import (
    DeletedPlaylistError,
    ExtractionError,
    ExtractionTimeoutError,
    NetworkError,
    PrivatePlaylistError,
    RateLimitedError,
    UnsupportedUrlError,
)


def classify_extraction_error(error: BaseException) -> ExtractionError:
    """Classify an exception by message while preserving user-friendly errors."""
    message = str(error).lower()
    if "429" in message or "too many requests" in message or "rate-limit" in message:
        return RateLimitedError(details=str(error))
    if "private" in message:
        return PrivatePlaylistError(details=str(error))
    if "deleted" in message or "does not exist" in message or "not found" in message:
        return DeletedPlaylistError(details=str(error))
    if "timed out" in message or "timeout" in message:
        return ExtractionTimeoutError(details=str(error))
    if "network" in message or "connection" in message or "temporary failure" in message:
        return NetworkError(details=str(error))
    if "unsupported url" in message or "unsupported" in message:
        return UnsupportedUrlError(details=str(error))
    return ExtractionError(details=str(error))
