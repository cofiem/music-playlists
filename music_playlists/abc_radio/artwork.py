from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.size import Size


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Artwork:
    entity: str
    arid: str
    url: str
    title: Optional[str]
    mini_synopsis: Optional[str]
    short_synopsis: Optional[str]
    medium_synopsis: Optional[str]
    sizes: Optional[list[Size]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    type: Optional[str] = None
    service_id: Optional[str] = None
