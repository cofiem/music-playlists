from dataclasses import dataclass
from typing import Optional

from music_playlists.intermediate.track import Track


@dataclass
class TrackList:
    type: str
    """The type of track list: 'ordered', 'all-plays'."""

    title: Optional[str]

    tracks: list[Track]

    @classmethod
    def type_ordered(cls):
        return "ordered"

    @classmethod
    def type_all_plays(cls):
        return "all-plays"
