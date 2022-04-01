import logging
from datetime import tzinfo, datetime, timedelta

import requests
from requests import Response

from music_playlists.downloader import Downloader
from music_playlists.intermediate.track import Track as ImmTrack
from music_playlists.intermediate.track_list import TrackList
from music_playlists.radio_4zzz.episode import Episode
from music_playlists.radio_4zzz.episode_summary import EpisodeSummary
from music_playlists.radio_4zzz.program import Program
from music_playlists.radio_4zzz.program_summary import ProgramSummary
from music_playlists.radio_4zzz.track import Track


class Manage:

    code = "radio-4zzz"

    _logger = logging.getLogger(code)

    def __init__(self, downloader: Downloader, time_zone: tzinfo):
        self._dl = downloader
        self._tz = time_zone
        self._url = "https://airnet.org.au/rest/stations/4ZZZ/programs"

    def active_program_tracks(self) -> TrackList:
        self._logger.info("Get Radio 4zzz Recently Played.")

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
                            title=t.title,
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

    def programs(self) -> list[ProgramSummary]:
        r = self._dl.get_session.get(self._url)
        self._check_response(r)
        return ProgramSummary.schema().load(r.json(), many=True)

    def program(self, program_summary: ProgramSummary) -> Program:
        if not program_summary:
            raise ValueError()
        if program_summary.program_rest_url.strip("/") == self._url:
            return None
        r = self._dl.get_session.get(program_summary.program_rest_url)
        self._check_response(r)
        return Program.from_dict(r.json())

    def episodes(self, program: Program) -> list[EpisodeSummary]:
        if not program:
            raise ValueError()

        r = self._dl.get_session.get(program.episodes_rest_url)
        self._check_response(r)
        return EpisodeSummary.schema().load(r.json(), many=True)

    def episode(self, episode_summary: EpisodeSummary) -> Episode:
        if not episode_summary:
            raise ValueError()

        r = self._dl.get_session.get(episode_summary.episode_rest_url)
        self._check_response(r)
        return Episode.from_dict(r.json())

    def playlist(self, episode: Episode) -> list[Track]:
        if not episode:
            raise ValueError()

        r = self._dl.get_session.get(episode.playlist_rest_url)
        self._check_response(r)
        return Track.schema().load(r.json(), many=True)

    def _episode_date(self, value: str):
        pat = "%Y-%m-%d %H:%M:%S"
        d1 = datetime.strptime(value, pat)
        d2 = d1.replace(tzinfo=self._tz)
        return d2

    def _check_response(self, r: Response):
        if r.status_code != requests.codes.ok or not r.text:
            raise ValueError(str(r))
