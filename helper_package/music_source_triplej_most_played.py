import logging
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode

from helper_package.data_helper import DataHelper


class MusicSourceTripleJMostPlayed:

    def __init__(self, data_helper: DataHelper = None):
        self._logger = logging.getLogger('music_playlists.MusicSourceTripleJMostPlayed')
        self._data_helper = data_helper or DataHelper()

        # https://music.abcradio.net.au/api/v1/recordings/plays.json?order=desc&limit=50&service=triplej&from=2019-10-12T13:00:00Z&to=2019-10-19T13:00:00Z
        self._url = 'https://music.abcradio.net.au/api/v1/recordings/plays.json?{qs}'

        self._gmusic_playlist_id = os.getenv('MUSIC_SOURCE_TRIPLEJ_MOST_PLAYED_PLAYLIST_ID')
        self._playlist_name = 'Triple J Most Played'
        self._group_id = 'triplej_most_played'

        self._url_date_format = '%Y-%m-%d'

    def run(self):
        current_time = datetime.today()

        url = self.build_url(date_from=current_time - timedelta(days=8), date_to=current_time - timedelta(days=1))
        data = self._data_helper.download_json(url)

        result = []
        for index, item in enumerate(data['items']):
            title = item['title']
            track_id = item['arid']

            artist = ''
            featuring = ''
            for raw_artist in item['artists']:
                if raw_artist['type'] == 'primary':
                    artist = f'{artist}, {raw_artist["name"]}'
                elif raw_artist['type'] == 'featured':
                    featuring = f'{artist}, {raw_artist["name"]}'
                else:
                    raise Exception(f"Unrecognised artist {raw_artist['type']}, {artist}, {raw_artist['name']}.")

            item = {
                'source': self._group_id,
                'source_playlist_title': self._playlist_name,
                'source_playlist_id': self._gmusic_playlist_id,
                'retrieved_at': current_time,
                'order': index + 1,
                'title': title,
                'artist': artist.strip(', '),
                'track_id': track_id,
                'featuring': featuring.strip(', ')
            }
            result.append(item)

        self._logger.info('Completed document')
        return result

    def build_url(self, date_from, date_to, order='desc', limit='50', service='triplej'):
        qs = urlencode({
            'order': order,
            'limit': limit,
            'service': service,
            'from': f'{date_from.strftime(self._url_date_format)}T13:00:00Z',
            'to': f'{date_to.strftime(self._url_date_format)}T13:00:00Z'
        })
        url = self._url.format(qs=qs)
        return url
