import logging
from pathlib import Path
from unittest import TestCase

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_source.radio4zzz_most_played import Radio4zzzMostPlayed


class TestMusicSourceRadio4zzzMostPlayed(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())

        cls._time_zone = pytz.timezone("Australia/Brisbane")

    def test_get_source_playlist(self):
        music_source = Radio4zzzMostPlayed(
            self._logger, self._downloader, self._time_zone
        )
        sources = music_source.get_playlist_tracks()

        current_highest_play_count = None
        for source in sources:
            play_count = source.info.get("play_count")
            if current_highest_play_count is None:
                current_highest_play_count = play_count

            # tracks are ordered as expected
            self.assertGreaterEqual(current_highest_play_count, play_count)
            current_highest_play_count = play_count

        # track_ids are unique
        self.assertEqual(len(sources), len(set(t.track_id for t in sources)))
