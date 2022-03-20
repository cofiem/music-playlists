import logging
import uuid
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

import pytz
from ytmusicapi import YTMusic

from music_playlists.downloader import Downloader
from music_playlists.music_service.youtube_music import YouTubeMusic


class TestServiceYouTubeMusic(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())
        cls._time_zone = pytz.timezone("Australia/Brisbane")
        cls._client = YouTubeMusic(cls._logger, cls._downloader, cls._time_zone)
        cls._client._client = YTMusic()

    def test_get_playlist_tracks(self):
        playlist_id = str(uuid.uuid4())
        track_id = "track id"
        track_title = "track title"
        artist_name = "artist name"

        mock = Mock(
            return_value={
                "tracks": [
                    {
                        "videoId": track_id,
                        "title": track_title,
                        "artists": [{"name": artist_name}],
                    }
                ]
            }
        )
        self._client._client.get_playlist = mock
        tracks = self._client.get_playlist_tracks(playlist_id)
        self.assertEqual(1, len(tracks))
        self.assertEqual(tracks[0].track_id, track_id)
        self.assertEqual(tracks[0].title, track_title)
        self.assertEqual(1, len(tracks[0].artists))
        self.assertEqual(tracks[0].artists[0], artist_name)

        mock.assert_called_once_with(playlist_id)

    def test_find_track(self):
        query = "track title"
        track_id = "track id"
        track_title = "track title"
        artist_name = "artist name"
        mock = Mock(
            return_value=[
                {
                    "videoId": track_id,
                    "title": track_title,
                    "artists": [{"name": artist_name}],
                }
            ]
        )
        self._client._client.search = mock
        tracks = self._client.find_track(query)
        self.assertEqual(1, len(tracks))
        self.assertEqual(tracks[0].track_id, track_id)
        self.assertEqual(tracks[0].title, track_title)
        self.assertEqual(1, len(tracks[0].artists))
        self.assertEqual(tracks[0].artists[0], artist_name)

        mock.assert_called_once_with(
            query=query, filter="songs", limit=5, ignore_spelling=False
        )
