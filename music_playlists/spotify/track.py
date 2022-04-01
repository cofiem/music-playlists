from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from music_playlists.spotify.album import Album
from music_playlists.spotify.artist import Artist
from music_playlists.spotify.external_id import ExternalId
from music_playlists.spotify.external_url import ExternalUrl
from music_playlists.spotify.restriction import Restriction


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Track:
    external_urls: ExternalUrl
    href: str
    id: str
    type: str
    uri: str
    name: Optional[str] = None
    album: Optional[Album] = None
    external_ids: Optional[ExternalId] = None
    popularity: Optional[int] = None
    track_number: Optional[int] = None
    is_local: Optional[bool] = None
    is_playable: Optional[bool] = None
    explicit: Optional[bool] = None
    duration_ms: Optional[int] = None
    disc_number: Optional[int] = None
    artists: list[Artist] = field(default_factory=list)
    preview_url: Optional[str] = None
    episode: Optional[bool] = None
    track: Optional[bool] = None
    restrictions: Optional[Restriction] = None
    linked_from: Optional["Track"] = None
    available_markets: Optional[list[str]] = None
