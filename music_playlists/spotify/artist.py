from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.spotify.external_url import ExternalUrl
from music_playlists.spotify.follower import Follower
from music_playlists.spotify.image import Image


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Artist:
    external_urls: ExternalUrl
    href: str
    id: str
    name: str
    type: str
    uri: str
    popularity: Optional[int] = None
    images: Optional[list[Image]] = None
    genres: Optional[list[str]] = None
    followers: Optional[list[Follower]] = None
