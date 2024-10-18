import attrs
from beartype import beartype


@beartype
@attrs.frozen
class Descriptors:
    """4zzz playlist track descriptors"""

    isAustralian: bool
    isLocal: bool
    isFemale: bool
    isIndigenous: bool
    isNew: bool
    isGenderNonConforming: bool | None


@beartype
@attrs.frozen
class Episode:
    """4zzz program episode"""

    notes: str | None
    start: str
    end: str
    duration: int
    url: str | None
    title: str | None
    imageUrl: str | None
    smallImageUrl: str | None
    playlistRestUrl: str


@beartype
@attrs.frozen
class EpisodeSummary:
    """4zzz episode summary"""

    url: str | None
    start: str
    end: str
    duration: int
    multipleEpsOnDay: bool
    title: str | None
    description: str | None
    imageUrl: str | None
    smallImageUrl: str | None
    episodeRestUrl: str
    currentEpisode: bool | None = False


@beartype
@attrs.frozen
class Program:
    """4zzz program"""

    url: str | None
    guideUrlOverride: str | None
    name: str
    broadcasters: str
    description: str | None
    gridDescription: str | None
    twitterHandle: str | None
    podcastUrl: str | None
    podcastUrl2: str | None
    defaultFirstAiredGuide: str
    slug: str
    bannerImageUrl: str | None
    bannerImageSmall: str | None
    profileImageUrl: str | None
    profileImageSmall: str | None
    facebookPage: str | None
    episodesRestUrl: str


@beartype
@attrs.frozen
class ProgramSummary:
    """4zzz program summary"""

    slug: str | None
    name: str
    broadcasters: str
    gridDescription: str | None
    archived: bool
    programRestUrl: str


@beartype
@attrs.frozen
class Testing:
    """4zzz playlist track testing"""

    date: str
    timezone_type: int
    timezone: str


@beartype
@attrs.frozen
class Track:
    """4zzz playlist track"""

    type: str
    id: int
    artist: str
    title: str | None
    track: str | None
    release: str | None
    time: str | None
    notes: str | None
    twitterHandle: str | None
    contentDescriptors: Descriptors
    wikipedia: str | None
    image: str | None
    video: str | None
    url: str | None
    approximateTime: str | None
    testing: Testing | None = None
    thispart: str | None = None
