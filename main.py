import logging
import os
import time
from logging.config import dictConfig
from os.path import abspath, join, dirname
from typing import List

import yaml

from helper_package.data_helper import DataHelper
from helper_package.music_source_triplej_most_played import MusicSourceTripleJMostPlayed
from helper_package.music_source_triplej_unearthed_chart import MusicSourceTripleJUnearthedChart
from helper_package.stream_playlist_google_music import StreamPlaylistGoogleMusic

# config logging
with open(abspath(join(dirname(abspath(__file__)), 'data', 'logging.yml')), 'rt') as f:
    config = yaml.safe_load(f)
    dictConfig(config)


class Processing:
    device_id = os.getenv('GMUSICAPI_DEVICE_ID')

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.Processing')
        self._data_helper = DataHelper()

        self._gmusic = StreamPlaylistGoogleMusic()

        self._triplej_unearthed_chart_data = MusicSourceTripleJUnearthedChart()
        self._triplej_unearthed_chart_gmusic_playlist_id = ''
        self._triplej_unearthed_chart_playlist_name = 'Triple J Unearthed Weekly Top 100'

        self._triplej_most_played_data = MusicSourceTripleJMostPlayed()
        self._triplej_most_played_gmusic_playlist_id = ''
        self._triplej_most_played_playlist_name = 'Triple J Most Played Daily Top 50'

    def run(self):
        self._logger.info('Starting...')

        # get the music sources
        triplej_unearthed_chart = self._triplej_unearthed_chart_data.run()
        triplej_most_played = self._triplej_most_played_data.run()

        # login to streaming service
        self._gmusic.login(self.device_id)

        # build the song playlist structure
        playlists = {}
        for item in triplej_unearthed_chart + triplej_most_played:
            source = item['source']
            order = item['order']
            if source not in playlists:
                playlists[source] = {}
            playlists[source][order] = {
                'retrieved_at': item['retrieved_at'],
                'order': item['order'],
                'title': item['title'],
                'artist': item['artist'],
                'track_id': item['track_id'],
                'featuring': item['featuring'],
            }

            # find the songs in the music streaming services
            self._logger.info(f"Finding \"{item['title']} - {item['artist']}\"...")
            gmusic_used_cache, gmusic_result = self._gmusic.query_song(item['title'], item['artist'], item['featuring'])
            gmusic_selected_song = self._gmusic.select_song(gmusic_result['song_hits'], item['title'], item['artist'])
            playlists[source][order]['gmusic'] = self._gmusic.build_result(gmusic_selected_song, item)

            if not gmusic_used_cache:
                # sleep so that the requests to the API aren't too much
                time.sleep(1)

        for playlist, songs in playlists.items():
            matches = []
            not_matches = []
            for index, song in songs.items():
                if song['gmusic']['track_id'] and song['gmusic']['match']:
                    matches.append(song)
                else:
                    not_matches.append(song)
            a = 1

        a = 1

    def _update_gmusic_playlist(self, playlist_id: str, playlist_name: str, playlist_description: str,
                                song_ids_old: List[str], song_ids_new: List[str]):
        """
        Generic playlist update
        """

        # rename existing playlist
        self._gmusic.playlist_update(playlist_id, playlist_name, playlist_description, public=True)

        # remove all songs
        self._gmusic.playlist_songs_remove(song_ids_old)

        # add new set of songs
        self._gmusic.playlist_songs_add(playlist_id, song_ids_new)


processing = Processing()
processing.run()
