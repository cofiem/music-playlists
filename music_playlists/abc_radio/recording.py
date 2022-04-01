from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.artist import Artist
from music_playlists.abc_radio.artwork import Artwork
from music_playlists.abc_radio.link import Link
from music_playlists.abc_radio.release import Release


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Recording:
    entity: str
    arid: str
    title: str
    metadata: Optional[str]
    description: Optional[str]
    duration: int
    artists: list[Artist]
    releases: list[Release]
    artwork: list[Artwork]
    links: list[Link]
