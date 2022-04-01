from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase, Undefined, config

from music_playlists.last_fm.artist import Artist
from music_playlists.last_fm.track_attr import TrackAttr
from music_playlists.last_fm.image import Image
from music_playlists.last_fm.streamable import Streamable


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Track:

    name: str
    duration: str
    listeners: str
    mbid: str
    url: str
    streamable: Streamable
    artist: Artist
    image: list[Image]
    attr: TrackAttr = field(metadata=config(field_name="@attr"))
