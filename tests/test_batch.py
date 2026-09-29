"""Tests for batch playlist processing helpers."""

from __future__ import annotations

import json
from pathlib import Path

from playlistforge.core.batch import BatchPlaylistInput, parse_batch_input, write_batch_json
from playlistforge.core.models import Playlist, Video


def _playlist() -> Playlist:
    return Playlist(
        playlist_id="PL1234567890",
        title="CS101 - Introduction to Computing",
        channel="Virtual University",
        webpage_url="https://www.youtube.com/playlist?list=PL1234567890",
        thumbnail=None,
        videos=(
            Video(
                lecture=1,
                playlist_index=1,
                title="Introduction",
                video_id="j8QdcI71-S4",
                watch_url="https://www.youtube.com/watch?v=j8QdcI71-S4",
                embed_url="https://www.youtube.com/embed/j8QdcI71-S4",
                thumbnail="https://i.ytimg.com/vi/j8QdcI71-S4/hqdefault.jpg",
            ),
        ),
    )


def test_parse_batch_input_with_course_codes_and_plain_urls() -> None:
    items = parse_batch_input(
        """
        CS101 | https://www.youtube.com/playlist?list=PL1111111111
        MTH101, https://www.youtube.com/playlist?list=PL2222222222
        https://www.youtube.com/playlist?list=PL3333333333
        """
    )

    assert [item.course_code for item in items] == ["CS101", "MTH101", None]
    assert items[0].output_stem == "CS101"
    assert items[2].output_stem == "PL3333333333"


def test_parse_batch_input_deduplicates_urls() -> None:
    url = "https://www.youtube.com/playlist?list=PL1111111111"
    assert len(parse_batch_input(f"CS101 | {url}\nCS101 | {url}")) == 1


def test_write_batch_json_checkpoints_course_metadata(tmp_path: Path) -> None:
    item = BatchPlaylistInput(
        course_code="CS101",
        url="https://www.youtube.com/playlist?list=PL1234567890",
    )

    path = write_batch_json(item, _playlist(), tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "CS101.json"
    assert payload["courseCode"] == "CS101"
    assert payload["playlist"]["playlistId"] == "PL1234567890"
    assert payload["playlist"]["videoCount"] == 1
    assert payload["videos"][0]["lecture"] == 1
    assert payload["videos"][0]["videoId"] == "j8QdcI71-S4"
    assert not path.with_suffix(".json.tmp").exists()
