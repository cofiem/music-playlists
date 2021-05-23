import logging
import uuid
from pathlib import Path
from unittest import TestCase

import pytz
import requests_mock

from music_playlists.downloader import Downloader
from music_playlists.music_service.spotify import Spotify
from music_playlists.music_service.spotify_client import SpotifyClient


class TestServiceSpotify(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())
        cls._time_zone = pytz.timezone("Australia/Brisbane")
        cls._client = Spotify(cls._logger, cls._downloader, cls._time_zone)
        cls._client._client = SpotifyClient(cls._logger, str(uuid.uuid4()))

    def test_get_playlist_tracks(self):
        playlist_id = str(uuid.uuid4())
        track_id = "track id"
        track_title = "track title"
        artist_name = "artist name"
        with requests_mock.Mocker() as m:
            m.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items%28track%28name%2Cid%2Cartists%28name%29%29%29&market=AU&offset=0",
                json={
                    "items": [
                        {
                            "track": {
                                "id": track_id,
                                "name": track_title,
                                "artists": [{"name": artist_name}],
                            }
                        }
                    ]
                },
            )
            tracks = self._client.get_playlist_tracks(playlist_id)
            self.assertEqual(1, len(tracks))
            self.assertEqual(tracks[0].track_id, track_id)
            self.assertEqual(tracks[0].title, track_title)
            self.assertEqual(1, len(tracks[0].artists))
            self.assertEqual(tracks[0].artists[0], artist_name)

    def test_find_track(self):
        query = "track title"
        track_id = "track id"
        track_title = "track title"
        artist_name = "artist name"
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.spotify.com/v1/search?q=track+title&limit=5&offset=0&type=track&market=AU",
                json={
                    "tracks": {
                        "items": [
                            {
                                "id": track_id,
                                "name": track_title,
                                "artists": [{"name": artist_name}],
                            }
                        ]
                    }
                },
            )
            used_cache, tracks = self._client.find_track(query)
            self.assertEqual(1, len(tracks))
            self.assertEqual(tracks[0].track_id, track_id)
            self.assertEqual(tracks[0].title, track_title)
            self.assertEqual(1, len(tracks[0].artists))
            self.assertEqual(tracks[0].artists[0], artist_name)
