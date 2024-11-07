import logging
from datetime import tzinfo, datetime, timedelta

import requests
from beartype import beartype
from requests import Response

from music_playlists.downloader import Downloader
from music_playlists.intermediate.models import TrackList, Track as ImmTrack
from music_playlists.intermediate.serialization import c
from music_playlists.radio_4zzz import models


logger = logging.getLogger("radio-4zzz-manage")


@beartype
class Manage:
    code = "radio-4zzz"

    def __init__(self, downloader: Downloader, time_zone: tzinfo):
        self._dl = downloader
        self._tz = time_zone
        self._url = "https://airnet.org.au/rest/stations/4ZZZ/programs"

    def active_program_tracks(self) -> TrackList:
        logger.info("Get Radio 4zzz Recently Played.")

        current_time = datetime.now(tz=self._tz)
        date_from = current_time - timedelta(days=7)
        date_to = current_time

        results = []

        for ps in self.programs():
            if ps.archived is not False:
                continue
            p = self.program(ps)
            if not p:
                continue
            for es in self.episodes(p):
                # must be fully inside the 'from date' -> 'to date'
                episode_start = self._episode_date(es.start)
                episode_end = self._episode_date(es.end)
                if episode_start < date_from or episode_end > date_to:
                    continue

                e = self.episode(es)
                for t in self.playlist(e):
                    results.append(
                        ImmTrack(
                            title=t.title or "",
                            artists=[t.artist],
                            origin_code=self.code,
                            raw=t,
                        )
                    )

        tl = TrackList(
            title="4zzz Most Played Weekly",
            type=TrackList.type_all_plays(),
            tracks=results,
        )
        return tl

    def programs(self) -> list[models.ProgramSummary]:
        r = self._dl.get_session.get(self._url)
        self._check_response(r)
        return c.structure(r.json(), list[models.ProgramSummary])

    def program(self, program_summary: models.ProgramSummary) -> models.Program | None:
        if not program_summary:
            raise ValueError()
        if program_summary.programRestUrl.strip("/") == self._url:
            return None
        r = self._dl.get_session.get(program_summary.programRestUrl)
        self._check_response(r)
        return c.structure(r.json(), models.Program)

    def episodes(self, program: models.Program) -> list[models.EpisodeSummary]:
        if not program:
            raise ValueError()

        r = self._dl.get_session.get(program.episodesRestUrl)
        self._check_response(r)
        return c.structure(r.json(), list[models.EpisodeSummary])

    def episode(self, episode_summary: models.EpisodeSummary) -> models.Episode:
        if not episode_summary:
            raise ValueError()

        r = self._dl.get_session.get(episode_summary.episodeRestUrl)
        self._check_response(r)
        return c.structure(r.json(), models.Episode)

    def playlist(self, episode: models.Episode) -> list[models.Track]:
        if not episode:
            raise ValueError()

        r = self._dl.get_session.get(episode.playlistRestUrl)
        self._check_response(r)
        return c.structure(r.json(), list[models.Track])

    def _episode_date(self, value: str):
        pat = "%Y-%m-%d %H:%M:%S"
        d1 = datetime.strptime(value, pat)
        d2 = d1.replace(tzinfo=self._tz)
        return d2

    def _check_response(self, r: Response):
        if r.status_code != requests.codes.ok or not r.text:
            raise ValueError(str(r))
