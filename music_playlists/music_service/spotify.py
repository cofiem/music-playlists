import logging
from typing import List, Optional

import requests

from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_service.spotify_client import SpotifyClient
from music_playlists.track import Track


class Spotify(ServicePlaylist):
    code = "spotify"

    def __init__(self, logger: logging.Logger, downloader: Downloader, time_zone):
        self._logger = logger
        self._time_zone = time_zone
        self._downloader = downloader
        self._client = None  # type: Optional[SpotifyClient]

    def login_init(self, client_id: str, client_secret: str):
        self._logger.info("Initialise Spotify login.")

        if not client_id or not client_secret:
            raise Exception("Must provide client_id and client_secret.")

        self._client = SpotifyClient(self._logger)
        access_token, refresh_token, expires_in = self._client.login_init(
            client_id, client_secret
        )

        self._logger.warning(f"Spotify access_token: {access_token}")
        self._logger.warning(f"Spotify refresh_token: {refresh_token}")
        self._logger.warning(f"Spotify expires_in: {expires_in / 60.0 / 60.0} hours")

        return access_token and refresh_token

    def login(self, refresh_token: str, client_id: str, client_secret: str) -> bool:
        self._logger.info("Login to Spotify.")
        if not refresh_token or not client_id or not client_secret:
            raise Exception("Must provide refresh_token, client_id, and client_secret.")
        self._client = SpotifyClient(self._logger)
        result = self._client.login_token_next(client_id, client_secret, refresh_token)
        return result

    def get_playlist_tracks(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> List[Track]:
        self._logger.info(f"Getting tracks for Spotify playlist '{playlist_id}'.")
        status, content = self._client.get_playlist_tracks(playlist_id, limit)
        result = []
        for item in content.get("items", []):
            track = item.get("track", {})
            result.append(
                Track(
                    origin_code=self.code,
                    track_id=track.get("id"),
                    title=track.get("name"),
                    artists=[a.get("name") for a in track.get("artists")],
                    info=track,
                    query_strings=[],
                )
            )
        return result

    def set_playlist_tracks(
        self, playlist_id: str, new_tracks: List[Track], old_tracks: List[Track]
    ) -> bool:
        self._logger.info(
            f"Setting {len(new_tracks)} tracks for Spotify playlist '{playlist_id}'."
        )
        status, content = self._client.set_playlist_tracks(
            playlist_id, [t.track_id for t in new_tracks]
        )
        return status == requests.codes.created

    def set_playlist_details(
        self,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        self._logger.info(f"Setting details for Spotify playlist '{playlist_id}'.")
        status, content = self._client.set_playlist_details(
            playlist_id, title, description, is_public
        )
        return status == requests.codes.ok

    def find_track(self, query: str, limit: int = 5) -> tuple[bool, list[Track]]:
        self._logger.debug(f"Looking for Spotify track matching '{query}'")
        cache_persist = self._downloader.cache_persisted
        used_cache = False
        tracks = []
        # cache response and use cache if available
        key = f"{self.code}api query {query}"
        query_result = self._downloader.retrieve_object(cache_persist, key)
        if query_result is not None:
            used_cache = True
            query_result = query_result.get_value()
        else:
            query_status, query_result = self._client.query(query, limit)
            self._downloader.store_object(cache_persist, key, query_result)

        # stop if there are results
        if query_result and query_result["tracks"].get("items"):
            for song_hit in query_result["tracks"].get("items"):
                track = Track(
                    origin_code=self.code,
                    track_id=song_hit.get("id"),
                    title=song_hit.get("name"),
                    artists=[artist.get("name") for artist in song_hit.get("artists")],
                    info=song_hit,
                    query_strings=[],
                )

                tracks.append(track)
        return used_cache, tracks
