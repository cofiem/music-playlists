from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.spotify.artist import Artist
from music_playlists.spotify.external_url import ExternalUrl
from music_playlists.spotify.image import Image


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Album:
    album_type: str
    total_tracks: int
    external_urls: ExternalUrl
    href: str
    id: str
    images: list[Image]
    name: str
    release_date: str
    release_date_precision: str
    type: str
    uri: str
    album_group: Optional[str] = None
    artists: Optional[list[Artist]] = None
    available_markets: Optional[list[str]] = None
