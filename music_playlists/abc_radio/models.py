import attrs
from beartype import beartype


@beartype
@attrs.frozen
class Size:
    url: str
    width: int
    height: int
    aspect_ratio: str


@beartype
@attrs.frozen
class Artwork:
    entity: str
    arid: str
    url: str
    title: str | None
    mini_synopsis: str | None
    short_synopsis: str | None
    medium_synopsis: str | None
    sizes: list[Size] | None = None
    width: int | None = None
    height: int | None = None
    type: str | None = None
    service_id: str | None = None
    is_primary: bool | None = None


@beartype
@attrs.frozen
class Link:
    entity: str
    arid: str
    url: str
    id_component: str | None
    title: str
    mini_synopsis: str | None
    short_synopsis: str | None
    medium_synopsis: str | None
    type: str
    provider: str
    external: bool
    service_id: str | None = None


@beartype
@attrs.frozen
class Artist:
    entity: str
    arid: str
    name: str
    artwork: list[Artwork]
    links: list[Link]
    type: str
    role: str | None = None
    is_australian: bool | None = False


@beartype
@attrs.frozen
class Release:
    entity: str
    arid: str | None
    title: str | None
    format: str | None
    artwork: list[Artwork]
    links: list[Link]
    record_label: str | None
    release_year: str | None
    artists: list[Artist] | None
    release_album_id: str | None
    is_primary: bool | None


@beartype
@attrs.frozen
class Recording:
    entity: str
    arid: str
    title: str
    metadata: str | None
    description: str | None
    duration: int
    artists: list[Artist]
    releases: list[Release]
    artwork: list[Artwork]
    links: list[Link]
    countdown: str | None = None


@beartype
@attrs.frozen
class Play:
    entity: str
    arid: str
    played_time: str
    service_id: str
    recording: Recording
    release: Release | None = None
    count: int | None = None


@beartype
@attrs.frozen
class Plays:
    total: int
    offset: int
    limit: int
    items: list[Recording]


@beartype
@attrs.frozen
class Search:
    total: int
    offset: int
    items: list[Play]


@beartype
@attrs.frozen
class UnearthedImage:
    """Unearthed Image."""

    url: str


@beartype
@attrs.frozen
class UnearthedArtist:
    """UnearthedArtist"""

    profileName: str
    slug: str
    image: UnearthedImage | None = None


@beartype
@attrs.frozen
class UnearthedSourceFile:
    """Unearthed SourceFile."""

    fileName: str
    url: str
    durationMs: int


@beartype
@attrs.frozen
class UnearthedTrack:
    """Unearthed Track."""

    id: str
    title: str
    codename: str
    explicit: bool
    uploadedOn: str
    playedOn: list[str]
    genres: list[str]
    webSourceFile: UnearthedSourceFile
    artist: UnearthedArtist
    image: UnearthedImage | None = None


@beartype
@attrs.frozen
class UnearthedTracksShowcase:
    trackOfTheDay: UnearthedTrack
    popularTracks: list[UnearthedTrack]
    discoverTracks: list[UnearthedTrack]
