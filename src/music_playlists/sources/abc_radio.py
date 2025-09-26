import logging

from datetime import date, datetime, timedelta

import attrs
import requests

from beartype import beartype

from music_playlists import intermediate as inter
from music_playlists import model, utils


logger = logging.getLogger(__name__)


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
    is_primary: bool | None = None


@beartype
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
    summary: str | None = None


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
    limit: int
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


@beartype
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

        # https://www.abc.net.au/triplej/featured-music/recently-played/
        # https://www.abc.net.au/doublej/featured-music/most-played/
        # https://www.abc.net.au/triplejunearthed/music/

    def triplej_most_played(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        plays = self.recordings_plays(
            "triplej",
            date_from,
            date_to,
            limit=100,
            refresh=refresh,
        )
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=self._convert_plays(plays),
        )
        return tl

    def doublej_most_played(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        plays = self.recordings_plays(
            "doublej",
            date_from,
            date_to,
            limit=100,
            refresh=refresh,
        )
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=self._convert_plays(plays),
        )
        return tl

    def unearthed_most_played(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        showcase = self.tracks_showcase(refresh=refresh)
        first = self._convert_unearthed_track(showcase.trackOfTheDay)
        second = [self._convert_unearthed_track(t) for t in showcase.popularTracks]
        third = [self._convert_unearthed_track(t) for t in showcase.discoverTracks]
        results = [first] + second + third
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=results,
        )
        return tl

    def classic_recently_played(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service="classic",
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
                refresh=refresh,
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

    def jazz_recently_played(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service="jazz",
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
                refresh=refresh,
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
        date_from: date,
        date_to: date,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        refresh=False,
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
        r = self._dl.get_session.get(
            self._url_recordings_plays, params=params, refresh=refresh
        )
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), Plays)
        raise ValueError(str(r))

    def plays_search(
        self,
        service: str,
        date_from: date,
        date_to: date,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        refresh=False,
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
        r = self._dl.get_session.get(
            self._url_plays_search, params=params, refresh=refresh
        )
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), Search)
        raise ValueError(str(r))

    def tracks_showcase(self, refresh=False) -> UnearthedTracksShowcase:
        """Get the unearthed featured tracks."""
        r = self._dl.get_session.get(self._url_tracks_showcase, refresh=refresh)
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json(), UnearthedTracksShowcase)
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
