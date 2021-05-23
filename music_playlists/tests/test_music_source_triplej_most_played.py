import logging
from pathlib import Path
from unittest import TestCase

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_source.triplej_most_played import TripleJMostPlayed


class TestMusicSourceTripleJMostPlayed(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())
        cls._time_zone = pytz.timezone("Australia/Brisbane")

    def test_get_source_playlist(self):
        music_source = TripleJMostPlayed(
            self._logger, self._downloader, self._time_zone
        )
        sources = music_source.get_playlist_tracks()

        self.assertEqual(50, len(sources))

        for index, source in enumerate(sources):
            # tracks are ordered as expected
            self.assertEqual(index + 1, source.info.get("source_order"))

        # track_ids are unique
        self.assertEqual(len(sources), len(set(t.track_id for t in sources)))
