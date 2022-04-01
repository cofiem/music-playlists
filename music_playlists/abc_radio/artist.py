from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.artwork import Artwork
from music_playlists.abc_radio.link import Link


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Artist:
    entity: str
    arid: str
    name: str
    artwork: list[Artwork]
    links: list[Link]
    type: str
    role: Optional[str] = None
    is_australian: Optional[bool] = False
