import logging
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import urlencode

from boltons.strutils import slugify

from music_playlists.downloader import Downloader


class TripleJMostPlayed:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'Double J Most Played Daily',
            'service': 'doublej',
            'gmusic_playlist_id': 'GOOGLE_MUSIC_PLAYLIST_DOUBLEJ_MOST_PLAYED_ID',
        },
        {
            'title': 'Triple J Most Played Daily',
            'service': 'triplej',
           'gmusic_playlist_id': 'GOOGLE_MUSIC_PLAYLIST_TRIPLEJ_MOST_PLAYED_ID',
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader

        # https://music.abcradio.net.au/api/v1/recordings/plays.json?order=desc&limit=50&service=doublej&from=2019-11-12T13:00:00Z&to=2019-11-19T13:00:00Z
        self._url = 'https://music.abcradio.net.au/api/v1/recordings/plays.json?{qs}'
        self._time_zone = time_zone

    def run(self, playlist_data: Dict[str, str]):
        self._logger.info(f"Started '{playlist_data['title']}'")
        current_time = datetime.now(tz=self._time_zone)
        current_day = current_time.date()

        url = self.build_url(playlist_data['service'], date_from=current_day - timedelta(days=8), date_to=current_day - timedelta(days=1))
        data = self._downloader.download_json(url)

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
                'playlist': playlist_data,
                'retrieved_at': current_time,
                'order': index + 1,
                'track': title,
                'artist': artist.strip(', '),
                'track_id': track_id,
                'featuring': featuring.strip(', '),
                'services': {},
            }
            result.append(item)

        self._logger.info(f"Completed '{playlist_data['title']}'")
        return result

    def build_url(self, service, date_from, date_to, order='desc', limit='50'):
        qs = urlencode({
            'order': order,
            'limit': limit,
            'service': service,
            'from': f"{date_from.strftime('%Y-%m-%d')}T13:00:00Z",
            'to': f"{date_to.strftime('%Y-%m-%d')}T13:00:00Z"
        })
        url = self._url.format(qs=qs)
        return url
