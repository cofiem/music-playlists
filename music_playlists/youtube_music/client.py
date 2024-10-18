import functools
import json
import logging
from pathlib import Path


import ytmusicapi.helpers
from ytmusicapi import YTMusic

from music_playlists.downloader import Downloader

logger = logging.getLogger("youtube-music-client")


class Client:
    def __init__(self, downloader: Downloader, credentials: str | None = None):
        self._downloader = downloader
        self._credentials = self._build_expected_credentials(credentials)
        self._session = self._downloader.get_session
        self._api: YTMusic | None = None

    @property
    def api(self):
        if not self._api:
            raise ValueError("Log in to YouTube music first.")
        return self._api

    def login(self):
        if not self._credentials:
            self._get_credentials()

        logger.info("Login using YouTube Music credentials.")
        s = self._session
        s.request = functools.partial(s.request, timeout=30)
        self._api = YTMusic(auth=self._credentials, requests_session=s)

    def _get_credentials(self):
        logger.info("Get YouTube Music credentials.")

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

    def _build_expected_credentials(self, raw: str) -> dict:
        """check headers required for auth and build the credentials data"""
        data = {k.lower(): v for k, v in json.loads(raw).items()}
        result = ytmusicapi.helpers.initialize_headers()
        required = ["cookie", "x-goog-authuser", "authorization"]
        for item in required:
            if item not in data:
                msg = f"Missing required item in credentials '{item}'."
                raise ValueError(msg)
            result[item] = data.get(item)

        return result
