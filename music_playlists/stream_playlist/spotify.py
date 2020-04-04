import logging
from typing import List, Dict

from music_playlists.downloader import Downloader
from music_playlists.playlist_data import PlaylistData


class Spotify:
    _logger = logging.getLogger(__name__)

    def __init__(self, downloader: Downloader, playlist_data: PlaylistData):
        self._downloader = downloader
        self._playlist_data = playlist_data

    def query_songs(self, data: List[Dict]) -> None:
        pass

    def playlists_update(self, playlists: List) -> None:
        pass
