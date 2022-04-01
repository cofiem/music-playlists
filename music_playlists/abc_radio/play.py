from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.abc_radio.recording import Recording
from music_playlists.abc_radio.release import Release


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Play:
    entity: str
    arid: str
    played_time: str
    service_id: str
    recording: Recording
    release: Optional[Release]
    count: Optional[int] = None
