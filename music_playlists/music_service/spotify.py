import logging
from typing import List, Optional

from requests import codes

from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_service.spotify_client import SpotifyClient
from music_playlists.track import Track


class Spotify(ServicePlaylist):
    code = "spotify"

    def __init__(self, logger: logging.Logger, downloader: Downloader, time_zone):
        super().__init__(logger, downloader, time_zone)
        self._client = SpotifyClient(self._logger, self._downloader)

    def login_init(self, client_id: str, client_secret: str):
        self._logger.info("Initialise Spotify login.")

        if not client_id or not client_secret:
            raise Exception("Must provide client_id and client_secret.")

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

        result = self._client.login_token_next(client_id, client_secret, refresh_token)
        return result

    def get_playlist_tracks(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> List[Track]:
        self._logger.info(f"Retrieving tracks for Spotify playlist.")
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
        self._logger.info(f"Setting {len(new_tracks)} tracks for Spotify playlist.")
        status, content = self._client.set_playlist_tracks(
            playlist_id, [t.track_id for t in new_tracks]
        )
        return status == codes.created

    def set_playlist_details(
        self,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        self._logger.info(f"Setting details for Spotify playlist '{title}'.")
        status, content = self._client.set_playlist_details(
            playlist_id, title, description, is_public
        )
        return status == codes.ok

    def find_track(self, query: str, limit: int = 5) -> list[Track]:
        self._logger.debug(f"Looking for Spotify track matching '{query}'")

        tracks = []
        # cache response and use cache if available
        query_status, query_result = self._client.query(query, limit)

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
        return tracks
