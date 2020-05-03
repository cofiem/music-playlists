from pathlib import Path
from unittest import TestCase

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_source.radio4zzz_most_played import Radio4zzzMostPlayed


class TestMusicSourceRadio4zzzMostPlayed(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._downloader = Downloader(Path('.', '..', '..').resolve())
        cls._time_zone = pytz.timezone('Australia/Brisbane')

    def test_get_source_playlist(self):
        music_source = Radio4zzzMostPlayed(self._downloader, self._time_zone)
        sources = music_source.playlists()

        self.assertEqual(1, len(sources))

        for source in sources:
            source_playlist, service_playlists = source

            # expected service playlists and source playlist length
            self.assertEqual(2, len(service_playlists))
            self.assertTrue(len(source_playlist.tracks) <= 100)

            # tracks are ordered as expected
            source_playlist_play_counts = [t.info['play_count'] for t in source_playlist.tracks]
            for index, value in enumerate(source_playlist_play_counts):
                if index > 0:
                    self.assertTrue(value <= source_playlist_play_counts[index - 1],
                                    f"{value} <= {source_playlist_play_counts[index - 1]}")

            # track_ids are unique
            self.assertEqual(len(source_playlist.tracks), len([t.track_id for t in source_playlist.tracks]))
