import logging
from typing import List

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader


class Spotify:
    _logger = logging.getLogger(__name__)

    def __init__(self, downloader: Downloader, time_zone):
        self._time_zone = time_zone
        self._downloader = downloader

    def query_songs(self, data: List['Track']) -> None:
        pass

    def playlists_update(self, playlists: List) -> None:
        pass
