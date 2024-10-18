import logging

from beartype import beartype
from requests import Response, codes

from music_playlists.downloader import Downloader
from music_playlists.intermediate.models import TrackList, Track
from music_playlists.intermediate.serialization import c
from music_playlists.spotify.client import Client
from music_playlists.spotify import models

logger = logging.getLogger("spotify-manage")


@beartype
class Manage:
    code = "spotify"

    def __init__(self, downloader: Downloader, client: Client):
        self._downloader = downloader
        self._client = client
        self._session = self._downloader.get_session

        self._url_api = "https://api.spotify.com/v1"
        self._url_accounts = "https://accounts.spotify.com"

    @property
    def client(self):
        return self._client

    def playlist_tracks(
        self, playlist_id: str, limit: int = 100, offset: int = 0, market: str = "AU"
    ) -> models.Tracks:
        """Get the tracks in a playlist."""

        logger.info("Get playlist tracks from spotify.")

        if not playlist_id:
            raise ValueError()
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        if not market:
            market = "AU"

        url = f"{self._url_api}/playlists/{playlist_id}/tracks"
        params = {
            "fields": "items(track(*))",
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        return c.structure(
            {"items": [t["track"] for t in r.json()["items"]]}, models.Tracks
        )

    def search_tracks(
        self, query: str, limit: int = 5, offset: int = 0, market: str = "AU"
    ) -> TrackList:
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        if not market:
            market = "AU"

        url = f"{self._url_api}/search"
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "type": "track",
            "market": market,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        ts = c.structure(r.json()["tracks"], models.Tracks)
        results = [self._convert_track(t) for t in ts.items]
        return TrackList(title=None, type=TrackList.type_ordered(), tracks=results)

    def update_playlist_tracks(self, playlist_id: str, tracks: list[Track]):
        """Replace songs in a playlist."""
        logger.info("Update spotify playlist tracks.")

        url = f"{self._url_api}/playlists/{playlist_id}/tracks"
        params = {"uris": [t.raw.uri for t in tracks]}
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.put(url, json=params, headers=headers)
        self._check_status(r)
        # snapshot_id = r.get('snapshot_id')
        return r.status_code in [codes.created, codes.ok]

    def update_playlist_details(
        self, playlist_id: str, title: str, description: str, is_public: bool
    ):
        logger.info("Get spotify playlist details.")

        url = f"{self._url_api}/playlists/{playlist_id}"
        data = {
            "name": title,
            "description": description,
            "public": True if is_public else False,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.put(url, json=data, headers=headers)
        self._check_status(r)
        return r.status_code == codes.ok

    def _check_status(self, r: Response):
        expected_codes = [codes.ok, codes.created]
        if r.status_code not in expected_codes:
            raise ValueError(
                f"Error in response url '{r.url}' "
                f"status '{r.status_code}' content '{r.text}'."
            )

    def _convert_track(self, item: models.Track):
        return Track(
            title=item.name,
            artists=[a.name for a in item.artists],
            origin_code=self.code,
            raw=item,
        )
