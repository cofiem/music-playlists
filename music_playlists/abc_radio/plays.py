from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.recording import Recording


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Plays:
    total: int
    offset: int
    limit: int
    items: list[Recording]
