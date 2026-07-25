"""Application exceptions with user-friendly messages."""

from __future__ import annotations


class PlaylistForgeError(Exception):
    """Base class for recoverable application errors."""

    user_message = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None, *, details: str | None = None) -> None:
        super().__init__(message or self.user_message)
        self.details = details


class ValidationError(PlaylistForgeError):
    """Raised when user input cannot be validated."""

    user_message = "Please enter a valid YouTube playlist URL."


class ExtractionError(PlaylistForgeError):
    """Base class for extraction failures."""

    user_message = "Playlist extraction failed."


class ExtractionCancelled(ExtractionError):
    """Raised when the user cancels extraction."""

    user_message = "Extraction was cancelled."


class RateLimitedError(ExtractionError):
    """Raised when YouTube rate limits the request."""

    user_message = "YouTube is rate limiting requests. Please wait a while and try again."


class PrivatePlaylistError(ExtractionError):
    """Raised when a playlist is private."""

    user_message = "This playlist is private or cannot be accessed."


class DeletedPlaylistError(ExtractionError):
    """Raised when a playlist has been deleted."""

    user_message = "This playlist appears to have been deleted."


class NetworkError(ExtractionError):
    """Raised for network connectivity issues."""

    user_message = "Network connection failed. Check your connection and try again."


class ExtractionTimeoutError(ExtractionError):
    """Raised when extraction times out."""

    user_message = "The request timed out. Try again later."


class UnsupportedUrlError(ExtractionError):
    """Raised when yt-dlp cannot handle a URL."""

    user_message = "This URL is not supported."


class ExportError(PlaylistForgeError):
    """Raised when export fails."""

    user_message = "Export failed. Please choose another destination and try again."


class SettingsError(PlaylistForgeError):
    """Raised when settings cannot be loaded or saved."""

    user_message = "Settings could not be loaded or saved."
