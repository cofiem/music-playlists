import logging
import time
from datetime import datetime
from logging.config import dictConfig
from os.path import abspath, join, dirname

import yaml
from pytz import timezone

from helper_package.data_helper import DataHelper
from helper_package.music_source_triplej_most_played import MusicSourceTripleJMostPlayed
from helper_package.music_source_triplej_unearthed_chart import MusicSourceTripleJUnearthedChart
from helper_package.music_source_doublej_most_played import MusicSourceDoubleJMostPlayed
from helper_package.stream_playlist_google_music import StreamPlaylistGoogleMusic

# config logging
with open(abspath(join(dirname(abspath(__file__)), 'data', 'logging.yml')), 'rt') as f:
    config = yaml.safe_load(f)
    dictConfig(config)


class Processing:

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.Processing')
        self._data_helper = DataHelper(use_cache=False)

        self._gmusic = StreamPlaylistGoogleMusic(self._data_helper)

        self._triplej_unearthed_chart_data = MusicSourceTripleJUnearthedChart(self._data_helper)
        self._triplej_most_played_data = MusicSourceTripleJMostPlayed(self._data_helper)
        self._doublej_most_played_data = MusicSourceDoubleJMostPlayed(self._data_helper)

    def run(self):
        self._logger.info('Starting...')

        timezone_bne = timezone('Australia/Brisbane')
        current_date = datetime.now()
        current_date_local = current_date.astimezone(timezone_bne)

        # get the music sources
        triplej_most_played = self._triplej_most_played_data.run()
        triplej_unearthed_chart = self._triplej_unearthed_chart_data.run()
        doublej_most_played = self._doublej_most_played_data.run()

        # login to streaming service
        self._logger.info('Logging in...')

        # write gmusicapi login details
        self._gmusic.gmusic_login()

        # build the song select structure
        self._logger.info('Selecting songs...')
        song_container = {}
        for item in triplej_most_played + triplej_unearthed_chart + doublej_most_played:
            source = item['source']
            order = item['order']
            if source not in song_container:
                song_container[source] = {}
            song_container[source][order] = {
                'retrieved_at': item['retrieved_at'],
                'order': item['order'],
                'title': item['title'],
                'artist': item['artist'],
                'track_id': item['track_id'],
                'featuring': item['featuring'],
                'source_playlist_title': item['source_playlist_title'],
                'source_playlist_id': item['source_playlist_id'],
            }

            # find the songs in the music streaming services
            gmusic_used_cache, gmusic_result = self._gmusic.query_song(
                item['title'], item['artist'], item['featuring'])
            gmusic_selected_song = self._data_helper.select_song(
                gmusic_result['song_hits'], item['title'], item['artist'], item['featuring'])
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

        # update google music playlists
        self._gmusic.playlists_update(playlists)

        self._logger.info('...finished.')


processing = Processing()
processing.run()
