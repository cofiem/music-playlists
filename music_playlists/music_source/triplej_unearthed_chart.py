import logging
from datetime import datetime
from typing import Dict, List

from lxml import html

from music_playlists.downloader import Downloader


class TripleJUnearthedChart:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'Triple J Unearthed Weekly',
            'gmusic_playlist_id': 'GOOGLE_MUSIC_PLAYLIST_TRIPLEJ_UNEARTHED_ID',
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader
        self._url = 'https://www.triplejunearthed.com/discover/charts'
        self._time_zone = time_zone

    def run(self, playlist_data: Dict[str, str]) -> List[Dict[str, str]]:
        self._logger.info(f"Started '{playlist_data['title']}'")
        current_time = datetime.now(tz=self._time_zone)

        content_text = self._downloader.download_text(self._url)
        content_html = html.fromstring(content_text)

        result = []
        for row in content_html.xpath('//li[@class="track"]'):
            order = row.xpath('./div[@class="this_week"]/text()')[0].strip()
            title = row.xpath('./div[@class="track_title"]/text()')[0].strip()
            artist = row.xpath('./div[@class="artist"]/a/@title')[0].strip()

            track_id_xpath = './div[@class="play_actions"]/a[@class="play_download_large"]/@href'
            track_id = row.xpath(track_id_xpath)[0].strip().replace('/download/track/', '')

            item = {
                'playlist': playlist_data,
                'retrieved_at': current_time,
                'order': order,
                'track': title,
                'artist': artist,
                'track_id': track_id,
                'featuring': '',
                'services': {},
            }
            result.append(item)

        self._logger.info(f"Completed {playlist_data['title']}")
        return result
