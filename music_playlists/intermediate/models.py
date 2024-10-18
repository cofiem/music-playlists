from dataclasses import field

import attrs
from beartype import beartype


@beartype
@attrs.frozen
class Track:
    title: str
    artists: list[str]
    origin_code: str
    raw: object

    title_normalised: str | None = None
    artists_normalised: list[str] = field(default_factory=list)

    def __str__(self):
        c = self.origin_code
        t = self.title
        a = "', '".join(a for a in self.artists)
        return f"{c}: '{t}' - '{a}'"


@beartype
@attrs.frozen
class TrackList:
    type: str
    """The type of track list: 'ordered', 'all-plays'."""

    title: str | None

    tracks: list[Track]

    @classmethod
    def type_ordered(cls):
        return "ordered"

    @classmethod
    def type_all_plays(cls):
        return "all-plays"
