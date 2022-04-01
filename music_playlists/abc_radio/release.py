from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.artist import Artist
from music_playlists.abc_radio.artwork import Artwork
from music_playlists.abc_radio.link import Link


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Release:
    entity: str
    arid: Optional[str]
    title: Optional[str]
    format: Optional[str]
    artwork: list[Artwork]
    links: list[Link]
    record_label: Optional[str]
    release_year: Optional[str]
    artists: Optional[list[Artist]]
    release_album_id: Optional[str]
