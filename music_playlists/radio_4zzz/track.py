from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined

from music_playlists.radio_4zzz.descriptors import Descriptors
from music_playlists.radio_4zzz.testing import Testing


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Track:
    """4zzz playlist track"""

    type: str
    id: int
    artist: str
    title: Optional[str]
    track: Optional[str]
    release: Optional[str]
    time: Optional[str]
    notes: Optional[str]
    twitter_handle: Optional[str]
    content_descriptors: Descriptors
    wikipedia: Optional[str]
    image: Optional[str]
    video: Optional[str]
    url: Optional[str]
    approximate_time: Optional[str]
    testing: Optional[Testing] = None
    thispart: Optional[str] = None
