import datetime
import logging

import attrs
import beartype
import requests

from music_playlists import intermediate as inter
from music_playlists import model, utils
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override

logger = logging.getLogger(__name__)


@beartype.beartype
@attrs.frozen
class Size:
    url: str
    width: int
    height: int
    aspect_ratio: str


@beartype.beartype
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


@beartype.beartype
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


@beartype.beartype
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


@beartype.beartype
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
    is_primary: bool | None = None


@beartype.beartype
@attrs.frozen
class Recording:
    entity: str
    arid: str
    title: str
    metadata: str | None
    description: str | None
    duration: int | None
    artists: list[Artist]
    releases: list[Release]
    artwork: list[Artwork]
    links: list[Link]
    countdown: str | None = None


@beartype.beartype
@attrs.frozen
class Play:
    entity: str
    arid: str
    played_time: str
    service_id: str
    recording: Recording
    release: Release | None = None
    count: int | None = None
    summary: str | None = None


@beartype.beartype
@attrs.frozen
class Plays:
    total: int
    offset: int
    limit: int
    items: list[Recording]


@beartype.beartype
@attrs.frozen
class Search:
    total: int
    offset: int
    limit: int
    items: list[Play]


@beartype.beartype
@attrs.frozen
class UnearthedImage:
    """Unearthed Image."""

    url: str


@beartype.beartype
@attrs.frozen
class UnearthedArtist:
    """UnearthedArtist"""

    profileName: str
    slug: str
    image: UnearthedImage | None = None


@beartype.beartype
@attrs.frozen
class UnearthedSourceFile:
    """Unearthed SourceFile."""

    fileName: str
    url: str
    durationMs: int


@beartype.beartype
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


@beartype.beartype
@attrs.frozen
class UnearthedTracksShowcase:
    trackOfTheDay: UnearthedTrack
    popularTracks: list[UnearthedTrack]
    discoverTracks: list[UnearthedTrack]


@beartype.beartype
@attrs.frozen
class MostPlayedItemImage:
    imgSrc: str  # "https://www.abc.net.au/triplej/albums/dmas-mybabysplace.jpg"
    ratio: str  # ":"1x1"
    alt: str  # ":""
    srcSet: list  # ":[]}


@beartype.beartype
@attrs.frozen
class MostPlayedItem:
    pass
    id: str  # ":"mtOYlnn2Ag"
    title: str  # ":"My Baby's Place"
    artist: str  # ":"DMA'S"
    hasComposerLabel: bool  # ":false
    duration: int  # ":233
    cardImageFallbackType: str  # ":"triplej"
    expandedTitle: str  # ":"My Baby's Place"
    primaryPerformer: str  # ":"DMA'S"
    youTubeUrl: str  # ":"https://www.youtube.com/results?search_query=My%20Baby's%20Place%20DMA'S"
    spotifyUrl: str  # ":"https://open.spotify.com/search/My%20Baby's%20Place%20DMA'S"
    appleUrl: str  # ":"https://music.apple.com/au/search?term=My%20Baby's%20Place%20DMA'S"
    timestampType: str  # ":"default"
    timestampRelativeSR: str  # ":""
    isAustralian: bool  # ":true
    unearthedUrl: str | None = None
    cardImageProps: MostPlayedItemImage | None = None  # ":{
    release: str | None = None  # ":"My Baby's Place"
    label: str | None = None  # ":""
    year: str  | None = None # ":"2026"

utils.c.register_structure_hook(
    MostPlayedItem,
    make_dict_structure_fn(MostPlayedItem, utils.c),
)

@beartype.beartype
@attrs.frozen
class MostPlayedPagination:
    offset: int
    total: int
    size: int


@beartype.beartype
@attrs.frozen
class MostPlayedResult:
    items: list[MostPlayedItem]
    pagination: MostPlayedPagination
    station: str
    date_from: str
    date_to: str

utils.c.register_structure_hook(
    MostPlayedResult,
    make_dict_structure_fn(MostPlayedResult, utils.c, date_from=override(rename="from"), date_to=override(rename="to")),
)

@beartype.beartype
class Manage(model.Source):
    code = "abc-radio"

    @classmethod
    def available(cls):
        return {
            "doublej-most-played-daily": cls.doublej_most_played,
            "triplej-most-played-daily": cls.triplej_most_played,
            "unearthed-most-played-weekly": cls.unearthed_most_played,
            "jazz-recently-played": cls.jazz_recently_played,
            "classic-recently-played": cls.classic_recently_played,
        }

    def __init__(self, downloader: utils.Downloader, time_zone):
        self._dl = downloader
        self._tz = time_zone
        self._url_abc_radio = "https://music.abcradio.net.au/api/v1"
        self._url_recordings_plays = f"{self._url_abc_radio}/recordings/plays.json"
        self._url_plays_search = f"{self._url_abc_radio}/plays/search.json"
        self._url_tracks_showcase = (
            "https://www.abc.net.au/triplejunearthed/api/loader/TracksShowcaseLoader"
        )
        self._url_core_next_most_played = "https://www.abc.net.au/core-next/api/mostPlayed"

        # https://www.abc.net.au/core-next/api/mostPlayed?
        # station=TRIPLEJ&
        # offset=0&
        # size=100&
        # from=2026-04-12T14%3A00%3A00%2B00%3A00&
        # to=2026-04-19T14%3A00%3A00%2B00%3A00&
        # itemCap=100

        # https://www.abc.net.au/triplej/featured-music/recently-played/
        # https://www.abc.net.au/doublej/featured-music/most-played/
        # https://www.abc.net.au/triplejunearthed/music/
        # https://www.abc.net.au/triplej/most-played

    def triplej_most_played(self, title: str) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        plays = self.recordings_plays("triplej", date_from, date_to, limit=100)
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=self._convert_plays(plays),
        )
        return tl

    def doublej_most_played(self, title: str) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        plays = self.recordings_plays("doublej", date_from, date_to, limit=100)
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=self._convert_plays(plays),
        )
        return tl

    def unearthed_most_played(self, title: str) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        results = []
        size = 20
        offset = 0
        item_cap = 100
        while True:
            result = self.most_played_api(
                station="UNEARTHED",
                date_from=date_from,
                date_to=date_to,
                size=size,
                offset=offset,
                item_cap=item_cap,
            )
            results.extend([self._convert_most_played_item(p) for p in result.items])
            count = result.pagination.offset + len(result.items)
            if count < item_cap:
                offset += size
            else:
                break


        # showcase = self.tracks_showcase()
        # first = self._convert_unearthed_track(showcase.trackOfTheDay)
        # second = [self._convert_unearthed_track(t) for t in showcase.popularTracks]
        # third = [self._convert_unearthed_track(t) for t in showcase.discoverTracks]
        # results = [first] + second + third
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=results,
        )
        return tl

    def classic_recently_played(self, title: str) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service="classic",
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset
            )
            results.extend([self._convert_play(p) for p in search.items])
            count = search.offset + len(search.items)
            if count < search.total:
                offset += limit
            else:
                break

        tl = inter.TrackList(
            title=title, type=inter.TrackListType.ALL_PLAYS, tracks=results
        )
        return tl

    def jazz_recently_played(self, title: str) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service="jazz",
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset
            )
            results.extend([self._convert_play(p) for p in search.items])
            count = search.offset + len(search.items)
            if count < search.total:
                offset += limit
            else:
                break

        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ALL_PLAYS,
            tracks=results,
        )
        return tl

    def recordings_plays(
            self,
            service: str,
            date_from: datetime.date,
            date_to: datetime.date,
            order: str = "desc",
            limit: int = 50,
            offset: int = 0
    ) -> Plays:
        """Get the most played songs for a service."""
        params = {
            "order": order,
            "limit": limit,
            "offset": offset,
            "service": service,
            "from": f"{date_from.strftime('%Y-%m-%d')}T13:00:00Z",
            "to": f"{date_to.strftime('%Y-%m-%d')}T13:00:00Z",
        }
        r = self._dl.get(
            self._url_recordings_plays, params=params
        )
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), Plays)
        raise ValueError(str(r))

    def plays_search(
            self,
            service: str,
            date_from: datetime.date,
            date_to: datetime.date,
            order: str = "desc",
            limit: int = 50,
            offset: int = 0
    ) -> Search:
        """Get the recently played songs for a service."""
        params = {
            "station": service,
            "from": f"{date_from.strftime('%Y-%m-%d')}T14:00:00",
            "to": f"{date_to.strftime('%Y-%m-%d')}T13:59:59",
            "limit": limit,
            "order": order,
            "offset": offset,
        }
        r = self._dl.get(
            self._url_plays_search, params=params
        )
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), Search)
        raise ValueError(str(r))

    def tracks_showcase(self) -> UnearthedTracksShowcase:
        """Get the unearthed featured tracks."""
        r = self._dl.get(self._url_tracks_showcase)
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), UnearthedTracksShowcase)
        raise ValueError(str(r))

    def most_played_api(self,
                        station: str,
                        date_from: datetime.date,
                        date_to: datetime.date,
                        size: int = 50,
                        offset: int = 0,
                        item_cap: int = 50
                        ):
        params = {
            "station": station,
            "from": f"{date_from.strftime('%Y-%m-%d')}T14:00:00+00:00",
            "to": f"{date_to.strftime('%Y-%m-%d')}T14:00:00+00:00",
            "size": size,
            "offset": offset,
            "item_cap": item_cap,
        }
        r = self._dl.get(
            self._url_core_next_most_played, params=params
        )
        if r.status_code == requests.codes.ok and r.text:
            data = r.json()
            return utils.c.structure(data, MostPlayedResult)
        raise ValueError(str(r))

    def _convert_plays(self, plays: Plays):
        result = []
        for recording in plays.items:
            if recording:
                result.append(
                    inter.Track(
                        origin_code=self.code,
                        track_id=recording.arid,
                        title=recording.title,
                        artists=[artist.name for artist in recording.artists],
                        raw=recording,
                    ),
                )
        return result

    def _convert_play(self, item: Play):
        if item.recording:
            return inter.Track(
                origin_code=self.code,
                track_id=item.recording.arid,
                title=item.recording.title,
                artists=[artist.name for artist in item.recording.artists],
                raw=item.recording,
            )
        if item.release:
            return inter.Track(
                origin_code=self.code,
                track_id=item.release.arid,
                title=item.release.title,
                artists=[artist.name for artist in item.release.artists],
                raw=item.release,
            )

    def _convert_unearthed_track(self, item: UnearthedTrack):
        return inter.Track(
            origin_code=self.code,
            track_id=item.id,
            title=item.title,
            artists=[item.artist.profileName],
            raw=item,
        )

    def _convert_most_played_item(self, item: MostPlayedItem):
        return inter.Track(
            origin_code=self.code,
            track_id=item.id,
            title=item.title,
            artists=list({item.artist, item.primaryPerformer}),
            raw=item,
        )
