import logging
from datetime import date, datetime, timedelta

import requests

from music_playlists.abc_radio.play import Play
from music_playlists.abc_radio.plays import Plays
from music_playlists.abc_radio.search import Search
from music_playlists.abc_radio.unearthed_track import UnearthedTrack
from music_playlists.abc_radio.unearthed_tracks_showcase import UnearthedTracksShowcase
from music_playlists.downloader import Downloader
from music_playlists.intermediate.track import Track
from music_playlists.intermediate.track_list import TrackList


class Manage:

    code = "abc-radio"

    _logger = logging.getLogger(code)

    service_doublej = "doublej"
    service_triplej = "triplej"
    service_jazz = "jazz"
    service_classic = "classic"

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
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

    def triplej_most_played(self) -> TrackList:
        self._logger.info("Get ABC Triple J Most Played.")

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        plays = self.recordings_plays(
            self.service_triplej, date_from, date_to, limit=100
        )
        tl = TrackList(
            title="Triple J Most Played Daily",
            type=TrackList.type_ordered(),
            tracks=self._convert_plays(plays),
        )
        return tl

    def doublej_most_played(self) -> TrackList:
        self._logger.info("Get ABC Double J Most Played.")

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        plays = self.recordings_plays(
            self.service_doublej, date_from, date_to, limit=100
        )
        tl = TrackList(
            title="Double J Most Played Daily",
            type=TrackList.type_ordered(),
            tracks=self._convert_plays(plays),
        )
        return tl

    def unearthed_most_played(self) -> TrackList:
        self._logger.info("Get ABC Unearthed Most Played.")

        showcase = self.tracks_showcase()
        first = self._convert_unearthed_track(showcase.track_of_the_day)
        second = [self._convert_unearthed_track(t) for t in showcase.popular_tracks]
        third = [self._convert_unearthed_track(t) for t in showcase.discover_tracks]
        results = [first] + second + third
        tl = TrackList(
            title="Triple J Unearthed Weekly",
            type=TrackList.type_ordered(),
            tracks=results,
        )
        return tl

    def classic_recently_played(self) -> TrackList:
        self._logger.info("Get ABC Classic Recently Played.")

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        s = self.service_classic
        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service=s,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
            results.extend([self._convert_play(p) for p in search.items])
            count = search.offset + len(search.items)
            if count < search.total:
                offset += limit
            else:
                break

        tl = TrackList(type=TrackList.type_all_plays(), tracks=results)
        return tl

    def jazz_recently_played(self) -> TrackList:
        self._logger.info("Get ABC Jazz Recently Played.")

        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - timedelta(days=8)
        date_to = current_day - timedelta(days=1)

        s = self.service_jazz
        results = []
        limit = 100
        offset = 0
        while True:
            search = self.plays_search(
                service=s,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
            results.extend([self._convert_play(p) for p in search.items])
            count = search.offset + len(search.items)
            if count < search.total:
                offset += limit
            else:
                break

        tl = TrackList(type=TrackList.type_all_plays(), tracks=results)
        return tl

    def recordings_plays(
        self,
        service: str,
        date_from: date,
        date_to: date,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
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
        r = self._dl.get_session.get(self._url_recordings_plays, params=params)
        if r.status_code == requests.codes.ok and r.text:
            return Plays.from_dict(r.json())
        else:
            raise ValueError(str(r))

    def plays_search(
        self,
        service: str,
        date_from: date,
        date_to: date,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
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
        r = self._dl.get_session.get(self._url_plays_search, params=params)
        if r.status_code == requests.codes.ok and r.text:
            return Search.from_dict(r.json())
        else:
            raise ValueError(str(r))

    def tracks_showcase(self) -> UnearthedTracksShowcase:
        """Get the unearthed featured tracks."""
        r = self._dl.get_session.get(self._url_tracks_showcase)
        if r.status_code == requests.codes.ok and r.text:
            return UnearthedTracksShowcase.from_dict(r.json())
        else:
            raise ValueError(str(r))

    def _convert_plays(self, plays: Plays):
        result = []
        for recording in plays.items:
            if recording:
                result.append(
                    Track(
                        title=recording.title,
                        artists=[artist.name for artist in recording.artists],
                        origin_code=self.code,
                        raw=recording,
                    )
                )
        return result

    def _convert_play(self, item: Play):
        if item.recording:
            return Track(
                title=item.recording.title,
                artists=[artist.name for artist in item.recording.artists],
                origin_code=self.code,
                raw=item.recording,
            )
        elif item.release:
            return Track(
                title=item.release.title,
                artists=[artist.name for artist in item.release.artists],
                origin_code=self.code,
                raw=item.release,
            )

    def _convert_unearthed_track(self, item: UnearthedTrack):
        return Track(
            title=item.title,
            artists=[item.artist.profile_name],
            origin_code=self.code,
            raw=item,
        )
