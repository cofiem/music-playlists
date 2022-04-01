import logging
from datetime import tzinfo

import requests

from music_playlists.downloader import Downloader
from music_playlists.intermediate.track import Track as ImmTrack
from music_playlists.intermediate.track_list import TrackList
from music_playlists.last_fm.track import Track


class Manage:

    code = "last-fm"

    _logger = logging.getLogger(code)

    def __init__(self, downloader: Downloader, time_zone: tzinfo, api_key: str):
        self._dl = downloader
        self._tz = time_zone
        self._api_key = api_key
        self._url = "https://ws.audioscrobbler.com/2.0"

    def aus_top_tracks(self) -> TrackList:
        self._logger.info("Get LastFM Top Tracks Australia.")

        country = "australia"

        top = self.top_tracks(country)
        results = [
            ImmTrack(
                title=t.name, artists=[t.artist.name], origin_code=self.code, raw=t
            )
            for t in top
        ]
        tl = TrackList(
            title="Last.fm Most Popular Weekly",
            type=TrackList.type_ordered(),
            tracks=results,
        )
        return tl

    def top_tracks(
        self,
        country: str,
        output_format: str = "json",
        limit: bool = "50",
        page: str = "1",
    ) -> list[Track]:
        params = {
            "api_key": self._api_key,
            "method": "geo.gettoptracks",
            "country": country,
            "format": output_format,
            "limit": limit,
            "page": page,
        }
        r = self._dl.get_session.get(self._url, params=params)
        if r.status_code == requests.codes.ok and r.text:
            return Track.schema().load(r.json()["tracks"]["track"], many=True)
        else:
            raise ValueError(str(r))
