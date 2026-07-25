"""Deterministic title-cleaning pipeline."""

from __future__ import annotations

from dataclasses import replace

from playlistforge.cleaning.rules import compile_rule
from playlistforge.core.models import CleaningRules, Playlist, Video


class CleaningEngine:
    """Apply ordered cleaning rules to video titles."""

    def clean_title(self, title: str, rules: CleaningRules) -> str:
        """Return a cleaned title without mutating source data."""
        cleaned = title
        for definition in rules.rules:
            if not definition.enabled:
                continue
            cleaned = compile_rule(definition).apply(cleaned)
        return cleaned

    def preview_video(self, video: Video, rules: CleaningRules) -> Video:
        """Return a copy of a video with title_cleaned populated."""
        return replace(video, title_cleaned=self.clean_title(video.title, rules))

    def apply_playlist(self, playlist: Playlist, rules: CleaningRules) -> Playlist:
        """Return a playlist copy with cleaned titles."""
        videos = tuple(self.preview_video(video, rules) for video in playlist.videos)
        return replace(playlist, videos=videos)

    def reset_playlist(self, playlist: Playlist) -> Playlist:
        """Return a playlist copy with cleaned titles removed."""
        return replace(
            playlist,
            videos=tuple(replace(video, title_cleaned=None) for video in playlist.videos),
        )
