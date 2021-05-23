import logging
from pathlib import Path
from unittest import TestCase

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_source.triplej_unearthed_chart import TripleJUnearthedChart


class TestMusicSourceTripleJUnearthedChart(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = logging.getLogger(__name__)
        cls._downloader = Downloader(cls._logger, Path(".", "..").resolve())

    def test_get_source_playlist(self):
        music_source = TripleJUnearthedChart(self._logger, self._downloader)
        sources = music_source.get_playlist_tracks()

        self.assertEqual(100, len(sources))

        for index, source in enumerate(sources):
            # tracks are ordered as expected
            self.assertEqual(index + 1, int(source.info.get("source_order")))

        # track_ids are unique
        self.assertEqual(len(sources), len(set(t.track_id for t in sources)))
