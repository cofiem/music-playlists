import logging
import os
from pathlib import Path
from unittest import TestCase

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_source.last_fm_most_popular import LastFmMostPopular


class TestMusicSourceLastFmMostPopular(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())

    def test_get_source_playlist(self):
        music_source = LastFmMostPopular(
            self._logger, self._downloader, os.getenv("LASTFM_AUTH_API_KEY")
        )
        sources = music_source.get_playlist_tracks()

        self.assertEqual(50, len(sources))

        for index, source in enumerate(sources):
            # tracks are ordered as expected
            self.assertEqual(index, int(source.info.get("@attr").get("rank")))

        # track_ids are unique
        self.assertEqual(len(sources), len(set(t.track_id for t in sources)))
