from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from dataclasses_json import dataclass_json

if TYPE_CHECKING:
    from music_playlists.data.track import Track


@dataclass_json
@dataclass
class SourcePlaylist:
    """An ordered list of tracks from a music playlist source."""
    playlist_name: str
    tracks: List['Track'] = field(default_factory=list)
