from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.play import Play


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Search:
    total: int
    offset: int
    items: list[Play]
