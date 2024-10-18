from dataclasses import field
from typing import Optional

import attrs
from beartype import beartype


@beartype
@attrs.frozen
class ExternalUrl:
    spotify: str


@beartype
@attrs.frozen
class Image:
    url: str
    height: int
    width: int


@beartype
@attrs.frozen
class Follower:
    href: str
    total: int


@beartype
@attrs.frozen
class Artist:
    external_urls: ExternalUrl
    href: str
    id: str
    name: str
    type: str
    uri: str
    popularity: int | None = None
    images: Optional[list[Image]] = None
    genres: Optional[list[str]] = None
    followers: Optional[list[Follower]] = None


@beartype
@attrs.frozen
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
    album_group: str | None = None
    artists: Optional[list[Artist]] = None
    available_markets: Optional[list[str]] = None
    is_playable: bool | None = None


@beartype
@attrs.frozen
class ExternalId:
    isrc: str | None = None
    """International Standard Recording Code"""

    ean: str | None = None
    """"International Article Number"""

    upc: str | None = None
    """Universal Product Code"""


@beartype
@attrs.frozen
class Restriction:
    reason: str


@beartype
@attrs.frozen
class Track:
    external_urls: ExternalUrl
    href: str
    id: str
    type: str
    uri: str
    name: str | None = None
    album: Optional[Album] = None
    external_ids: Optional[ExternalId] = None
    popularity: int | None = None
    track_number: int | None = None
    is_local: bool | None = None
    is_playable: bool | None = None
    explicit: bool | None = None
    duration_ms: int | None = None
    disc_number: int | None = None
    artists: list[Artist] = field(default_factory=list)
    preview_url: str | None = None
    episode: bool | None = None
    track: bool | None = None
    restrictions: Optional[Restriction] = None
    linked_from: Optional["Track"] = None
    available_markets: Optional[list[str]] = None


@beartype
@attrs.frozen
class Tracks:
    items: list[Track]
    href: str | None = None
    limit: int | None = None
    next: str | None = None
    offset: int | None = None
    previous: str | None = None
    total: int | None = None