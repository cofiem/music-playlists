import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode

from helper_package.data_helper import DataHelper


class MusicSourceTripleJMostPlayed:
    # https://music.abcradio.net.au/api/v1/recordings/plays.json?order=desc&limit=50&service=triplej&from=2019-10-12T13:00:00Z&to=2019-10-19T13:00:00Z
    url = 'https://music.abcradio.net.au/api/v1/recordings/plays.json?{qs}'
    url_date_format = '%Y-%m-%d'
    data_helper = DataHelper()

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.MusicSourceTripleJMostPlayed')

    def run(self):
        current_time = datetime.today()

        self._logger.info(f'Loading Triple J most played at {current_time}')

        url = self.build_url(date_from=current_time - timedelta(days=7), date_to=current_time)
        data = self.data_helper.download_json(url)

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
                'source': 'triplej_most_played',
                'retrieved_at': current_time,
                'order': index + 1,
                'title': title,
                'artist': artist.strip(', '),
                'track_id': track_id,
                'featuring': featuring.strip(', ')
            }
            title, featuring = self.data_helper.normalise(item['title'], item['artist'])
            item['title'] = title
            item['featuring'] = featuring
            result.append(item)

        return result

    def build_url(self, date_from, date_to, order='desc', limit='50', service='triplej'):
        qs = urlencode({
            'order': order,
            'limit': limit,
            'service': service,
            'date_from': f'{date_from.strftime(self.url_date_format)}T13:00:00Z',
            'date_to': f'{date_to.strftime(self.url_date_format)}T13:00:00Z'
        })
        url = self.url.format(qs=qs)
        return url
