from typing import Optional

from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase, Undefined

from music_playlists.spotify.track import Track


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Tracks:
    items: list[Track]
    href: Optional[str] = None
    limit: Optional[int] = None
    next: Optional[str] = None
    offset: Optional[int] = None
    previous: Optional[str] = None
    total: Optional[int] = None
