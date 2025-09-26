import logging

from datetime import datetime, timedelta, tzinfo

import attrs
import requests

from beartype import beartype
from requests import Response

from music_playlists import intermediate as inter
from music_playlists import model, utils


logger = logging.getLogger(__name__)


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


@beartype
class Manage(model.Source):
    code = "radio-4zzz"

    @classmethod
    def available(cls):
        return {
            "all-most-played-weekly": cls.active_program_tracks,
        }

    def __init__(self, downloader: utils.Downloader, time_zone: tzinfo):
        self._dl = downloader
        self._tz = time_zone
        self._url = "https://airnet.org.au/rest/stations/4ZZZ/programs"

    def active_program_tracks(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        current_time = datetime.now(tz=self._tz)
        date_from = current_time - timedelta(days=7)
        date_to = current_time

        results = []

        for ps in self.programs(refresh=refresh):
            if ps.archived is not False:
                continue
            p = self.program(ps, refresh=refresh)
            if not p:
                continue
            for es in self.episodes(p, refresh=refresh):
                # must be fully inside the 'from date' -> 'to date'
                episode_start = self._episode_date(es.start)
                episode_end = self._episode_date(es.end)
                if episode_start < date_from or episode_end > date_to:
                    continue

                e = self.episode(es, refresh=refresh)
                for t in self.playlist(e, refresh=refresh):
                    results.append(
                        inter.Track(
                            origin_code=self.code,
                            track_id=str(t.id),
                            title=t.title or "",
                            artists=[t.artist],
                            raw=t,
                        ),
                    )

        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ALL_PLAYS,
            tracks=results,
        )
        return tl

    def programs(self, refresh=False) -> list[ProgramSummary]:
        r = self._dl.get_session.get(self._url, refresh=refresh)
        self._check_response(r)
        return utils.c.structure(r.json(), list[ProgramSummary])

    def program(self, program_summary: ProgramSummary, refresh=False) -> Program | None:
        if not program_summary:
            raise ValueError
        if program_summary.programRestUrl.strip("/") == self._url:
            return None
        r = self._dl.get_session.get(program_summary.programRestUrl, refresh=refresh)
        self._check_response(r)
        return utils.c.structure(r.json(), Program)

    def episodes(self, program: Program, refresh=False) -> list[EpisodeSummary]:
        if not program:
            raise ValueError

        r = self._dl.get_session.get(program.episodesRestUrl, refresh=refresh)
        self._check_response(r)
        return utils.c.structure(r.json(), list[EpisodeSummary])

    def episode(self, episode_summary: EpisodeSummary, refresh=False) -> Episode:
        if not episode_summary:
            raise ValueError

        r = self._dl.get_session.get(episode_summary.episodeRestUrl, refresh=refresh)
        self._check_response(r)
        return utils.c.structure(r.json(), Episode)

    def playlist(self, episode: Episode, refresh=False) -> list[Track]:
        if not episode:
            raise ValueError

        r = self._dl.get_session.get(episode.playlistRestUrl, refresh=refresh)
        self._check_response(r)
        return utils.c.structure(r.json(), list[Track])

    def _episode_date(self, value: str):
        pat = "%Y-%m-%d %H:%M:%S"
        d1 = datetime.strptime(value, pat)
        d2 = d1.replace(tzinfo=self._tz)
        return d2

    def _check_response(self, r: Response):
        if r.status_code != requests.codes.ok or not r.text:
            raise ValueError(str(r))
