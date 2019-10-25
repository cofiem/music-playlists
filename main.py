import json
import logging
import os
import time
from datetime import datetime
from logging.config import dictConfig
from os.path import abspath, join, dirname
from typing import List

import yaml
from pytz import timezone

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
        self._triplej_most_played_data = MusicSourceTripleJMostPlayed()

    def run(self):
        self._logger.info('Starting...')

        timezone_bne = timezone('Australia/Brisbane')
        current_date = datetime.now()
        current_date_local = current_date.astimezone(timezone_bne)

        # get the music sources
        triplej_unearthed_chart = self._triplej_unearthed_chart_data.run()
        triplej_most_played = self._triplej_most_played_data.run()

        # login to streaming service
        self._logger.info('Logging in...')
        self._gmusic.login(self.device_id)

        # build the song select structure
        self._logger.info('Selecting songs...')
        song_container = {}
        for item in triplej_unearthed_chart + triplej_most_played:
            source = item['source']
            order = item['order']
            if source not in song_container:
                song_container[source] = {}
            song_container[source][order] = {
                'retrieved_at': item['retrieved_at'],
                'order': item['order'],
                'title': item['title'],
                'title_compare': item['title_compare'],
                'artist': item['artist'],
                'track_id': item['track_id'],
                'featuring': item['featuring'],
                'source_playlist_title': item['source_playlist_title'],
                'source_playlist_id': item['source_playlist_id'],
            }

            # find the songs in the music streaming services
            gmusic_used_cache, gmusic_result = self._gmusic.query_song(
                item['title_compare'], item['artist'], item['featuring'])
            gmusic_selected_song = self._data_helper.select_song(
                gmusic_result['song_hits'], item['title_compare'], item['artist'])
            song_container[source][order]['gmusic'] = self._data_helper.build_result(gmusic_selected_song, item)

            if not gmusic_used_cache:
                # sleep so that the requests to the API aren't too much
                time.sleep(1)

        # build the playlist data
        self._logger.info('Building playlists...')
        playlists = []
        for playlist, songs in song_container.items():
            matches = {}
            not_matches = {}
            song = {}
            for index, song in songs.items():
                if song['gmusic']['track_id'] and song['gmusic']['match']:
                    matches[index] = song
                else:
                    not_matches[index] = song

            name_date = '%a, %d %b %Y'
            name = f"{song.get('source_playlist_title')} ({current_date_local.strftime(name_date)})"
            playlist_data = self._data_helper.build_playlist(matches, not_matches)
            playlists.append({
                'id': song.get('source_playlist_id'),
                'name': name,
                'description': playlist_data['description'],
                'song_ids_new': playlist_data['gmusic_song_ids'],
            })

        # get all gmusic playlists with songs
        gmusic_playlists_cache_key = 'gmusic all playlists with songs'
        gmusic_playlists = self._data_helper.cache_load_page(gmusic_playlists_cache_key)
        if not gmusic_playlists:
            gmusic_playlists = self._gmusic.playlists_songs()
            self._data_helper.cache_save_page(gmusic_playlists_cache_key, json.dumps(gmusic_playlists).encode('utf-8'))
        else:
            gmusic_playlists = json.loads(gmusic_playlists.decode('utf-8'))

        # update the streaming service playlists
        for playlist in playlists:

            song_ids_old = []
            for gmusic_playlist in gmusic_playlists:
                if gmusic_playlist['id'] == playlist['id']:
                    for t in gmusic_playlist.get('tracks', []):
                        if not t.get('track'):
                            continue
                        song_playlist_id = t['id']
                        song_track_id = t['track'].get('storeId') or t['track'].get('trackId') or \
                                        t['track'].get('id') or t['track'].get('nid')
                        song_ids_old.append((song_playlist_id, song_track_id))

            self._update_gmusic_playlist(playlist['id'], playlist['name'], playlist['description'],
                                         song_ids_old, playlist['song_ids_new'])

        self._logger.info('...finished.')

    def _update_gmusic_playlist(self, playlist_id: str, playlist_name: str, playlist_description: str,
                                song_ids_old: List[str], song_ids_new: List[str]):
        """
        Generic playlist update
        """

        # rename existing playlist
        self._gmusic.playlist_update(playlist_id, playlist_name, playlist_description, public=True)

        # remove songs not in song_ids_new
        song_track_ids_to_add = set(song_ids_new) - set([i[1] for i in song_ids_old])
        song_track_ids_to_remove = set([i[1] for i in song_ids_old]) - set(song_ids_new)
        song_playlist_ids_to_remove = [i[0] for i in song_ids_old if i[1] in song_track_ids_to_remove]
        if song_playlist_ids_to_remove:
            self._gmusic.playlist_songs_remove(song_playlist_ids_to_remove)

        # add new set of songs
        if song_track_ids_to_add:
            self._gmusic.playlist_songs_add(playlist_id, list(song_track_ids_to_add))


processing = Processing()
processing.run()
