import attrs
from beartype import beartype


@beartype
@attrs.frozen
class Album:
    name: str
    id: str


@beartype
@attrs.frozen
class Artist:
    name: str
    id: str | None = None
    type: str | None = None


@beartype
@attrs.frozen
class Author:
    name: str
    id: str


@beartype
@attrs.frozen
class Feedback:
    add: str | None
    remove: str | None


@beartype
@attrs.frozen
class Thumbnail:
    url: str
    width: int
    height: int


@beartype
@attrs.frozen
class Track:
    title: str
    artists: list[Artist]
    thumbnails: list[Thumbnail]
    isExplicit: bool
    duration: str | None = None
    duration_seconds: int | None = None
    videoId: str | None = None
    views: str | None = None
    album: Album | None = None
    feedbackTokens: Feedback | None = None
    isAvailable: bool | None = None
    likeStatus: str | None = None
    setVideoId: str | None = None
    year: str | None = None
    category: str | None = None
    resultType: str | None = None
    videoType: str | None = None
    inLibrary: bool | None = None


@beartype
@attrs.frozen
class Playlist:
    id: str
    privacy: str
    title: str
    thumbnails: list[Thumbnail]
    description: str
    # author: Author
    trackCount: int
    # suggestions_token: str
    tracks: list[Track]
    duration: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    related: str | None = None
    owned: str | None = None
    artists: str | None = None
    views: str | None = None


@beartype
@attrs.frozen
class Tracks:
    pass
