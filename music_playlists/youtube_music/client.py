import functools
import logging
from pathlib import Path
from typing import Optional

from ytmusicapi import YTMusic

from music_playlists.downloader import Downloader


class Client:
    _logger = logging.getLogger("youtube-music-client")

    def __init__(self, downloader: Downloader, credentials: Optional[str] = None):
        self._downloader = downloader
        self._credentials = credentials
        self._session = self._downloader.get_session
        self._api: Optional[YTMusic] = None

    @property
    def api(self):
        if not self._api:
            raise ValueError("Log in to YouTube music first.")
        return self._api

    def login(self):
        if not self._credentials:
            self._get_credentials()

        self._logger.info("Login using YouTube Music credentials.")
        s = self._session
        s.request = functools.partial(s.request, timeout=30)
        self._api = YTMusic(auth=self._credentials, requests_session=s)

    def _get_credentials(self):
        self._logger.info("Get YouTube Music credentials.")

        file_path = input(
            "Enter the file path to the request headers from https://music.youtube.com:"
        )
        if not file_path:
            raise ValueError("Provide the file path.")
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"Invalid file path '{path}'.")

        request_headers = path.read_text()
        self._credentials = YTMusic.setup(filepath=None, headers_raw=request_headers)
