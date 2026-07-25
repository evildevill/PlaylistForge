"""URL parsing and validation for playlist inputs."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playlistforge.core.enums import UrlType

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
PLAYLIST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{10,}$")


def classify_url(text: str) -> UrlType:
    """Classify a user-supplied string."""
    stripped = text.strip()
    if not stripped:
        return UrlType.UNKNOWN
    if Path(stripped).suffix.lower() == ".txt":
        return UrlType.TEXT_FILE
    parsed = urlparse(stripped)
    host = parsed.netloc.lower()
    if host not in YOUTUBE_HOSTS:
        return UrlType.UNKNOWN
    query = parse_qs(parsed.query)
    if "list" in query and query["list"] and PLAYLIST_ID_PATTERN.match(query["list"][0]):
        return UrlType.PLAYLIST
    if host == "youtu.be" or parsed.path.startswith("/watch"):
        return UrlType.VIDEO
    return UrlType.UNKNOWN


def normalize_playlist_url(text: str) -> str | None:
    """Return a canonical playlist URL, or None if the text is invalid."""
    stripped = text.strip()
    parsed = urlparse(stripped)
    query = parse_qs(parsed.query)
    playlist_id = query.get("list", [None])[0]
    if not playlist_id or not PLAYLIST_ID_PATTERN.match(playlist_id):
        return None
    return f"https://www.youtube.com/playlist?list={playlist_id}"


def extract_urls_from_text(text: str) -> tuple[str, ...]:
    """Extract and normalize playlist URLs from pasted text."""
    candidates = re.split(r"[\s,]+", text.strip())
    urls: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = normalize_playlist_url(candidate)
        if normalized and normalized not in seen:
            urls.append(normalized)
            seen.add(normalized)
    return tuple(urls)
