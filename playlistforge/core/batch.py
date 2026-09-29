"""Batch playlist input parsing and crash-safe JSON checkpoint writing."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playlistforge.core.models import ExportOptions, Playlist
from playlistforge.export.fields import rows_for_export

_COURSE_CODE_RE = re.compile(r"^[A-Za-z]{2,10}[ -]?\d{2,5}[A-Za-z]?$")
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(slots=True, frozen=True)
class BatchPlaylistInput:
    """One playlist in a batch, optionally labelled with a course code."""

    url: str
    course_code: str | None = None

    @property
    def output_stem(self) -> str:
        """Return a stable filesystem-safe output stem."""
        if self.course_code:
            return _SAFE_NAME_RE.sub("-", self.course_code.strip()).strip("-").upper()
        playlist_id = parse_qs(urlparse(self.url).query).get("list", ["playlist"])[0]
        return _SAFE_NAME_RE.sub("-", playlist_id).strip("-") or "playlist"


def parse_batch_input(text: str) -> tuple[BatchPlaylistInput, ...]:
    """Parse one batch item per line; preferred form is COURSE_CODE | URL."""
    items: list[BatchPlaylistInput] = []
    seen: set[str] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        course_code: str | None = None
        url: str | None = None

        if line.startswith(("http://", "https://")):
            url = line
        else:
            match = re.search(r"https?://\S+", line)
            if match:
                url = match.group(0).rstrip(",;")
                prefix = line[: match.start()].strip(" \t|,:;-")
                if prefix and _COURSE_CODE_RE.fullmatch(prefix):
                    course_code = prefix.replace(" ", "").upper()

        if not url or ("youtube.com" not in url.lower() and "youtu.be" not in url.lower()):
            continue
        if url in seen:
            continue
        seen.add(url)
        items.append(BatchPlaylistInput(url=url, course_code=course_code))

    return tuple(items)


def write_batch_json(
    item: BatchPlaylistInput,
    playlist: Playlist,
    destination_directory: Path,
    *,
    pretty: bool = True,
) -> Path:
    """Atomically checkpoint one completed playlist as JSON."""
    destination_directory.mkdir(parents=True, exist_ok=True)
    path = destination_directory / f"{item.output_stem}.json"
    temp_path = path.with_suffix(".json.tmp")
    options = ExportOptions(pretty_json=pretty)
    payload = {
        "courseCode": item.course_code,
        "playlist": {
            "playlistId": playlist.playlist_id,
            "title": playlist.title,
            "channel": playlist.channel,
            "webpageUrl": playlist.webpage_url,
            "thumbnail": playlist.thumbnail,
            "videoCount": playlist.video_count,
            "extractedAt": playlist.extracted_at.isoformat(),
        },
        "videos": rows_for_export((playlist,), options),
    }
    indent = 2 if pretty else None
    temp_path.write_text(
        json.dumps(payload, indent=indent, ensure_ascii=False),
        encoding="utf-8",
    )
    temp_path.replace(path)
    return path
