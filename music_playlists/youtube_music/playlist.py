from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, Undefined, config

from music_playlists.youtube_music.author import Author
from music_playlists.youtube_music.thumbnail import Thumbnail
from music_playlists.youtube_music.track import Track


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Playlist:
    id: str
    privacy: str
    title: str
    thumbnails: list[Thumbnail]
    description: str
    author: Author
    track_count: int = field(metadata=config(field_name="trackCount"))
    duration: str
    duration_seconds: int
    suggestions_token: str
    tracks: list[Track]
