import logging
from datetime import tzinfo

import requests
from beartype import beartype

from music_playlists.downloader import Downloader
from music_playlists.intermediate.models import TrackList, Track
from music_playlists.intermediate.serialization import c
from music_playlists.last_fm import models

logger = logging.getLogger("last-fm-manage")


@beartype
class Manage:
    code = "last-fm"

    def __init__(self, downloader: Downloader, time_zone: tzinfo, api_key: str):
        self._dl = downloader
        self._tz = time_zone
        self._api_key = api_key
        self._url = "https://ws.audioscrobbler.com/2.0"

    def aus_top_tracks(self) -> TrackList:
        logger.info("Get LastFM Top Tracks Australia.")

        country = "australia"

        top = self.top_tracks(country)
        results = [
            Track(title=t.name, artists=[t.artist.name], origin_code=self.code, raw=t)
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
    ) -> list[models.Track]:
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
            return c.structure(r.json()["tracks"]["track"], list[models.Track])
        else:
            raise ValueError(str(r))
