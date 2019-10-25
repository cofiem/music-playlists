import logging
import os
from datetime import datetime

from lxml import html

from helper_package.data_helper import DataHelper


class MusicSourceTripleJUnearthedChart:
    url = 'https://www.triplejunearthed.com/discover/charts'
    gmusic_playlist_id = os.getenv('MUSIC_SOURCE_TRIPLEJ_UNEARTHED_PLAYLIST_ID')
    playlist_name = 'Triple J Unearthed'
    group_id = 'triplej_unearthed_chart'

    url_date_format = '%Y-%m-%d'
    data_helper = DataHelper()

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.MusicSourceTripleJUnearthedChart')

    def run(self):
        current_time = datetime.today()

        content_text = self.data_helper.download_text(self.url)
        content_html = html.fromstring(content_text)

        result = []
        for row in content_html.xpath('//li[@class="track"]'):
            order = row.xpath('./div[@class="this_week"]/text()')[0].strip()
            title = row.xpath('./div[@class="track_title"]/text()')[0].strip()
            artist = row.xpath('./div[@class="artist"]/a/@title')[0].strip()

            track_id_xpath = './div[@class="play_actions"]/a[@class="play_download_large"]/@href'
            track_id = row.xpath(track_id_xpath)[0].strip().replace('/download/track/', '')

            item = {
                'source': self.group_id,
                'source_playlist_title': self.playlist_name,
                'source_playlist_id': self.gmusic_playlist_id,
                'retrieved_at': current_time,
                'order': order,
                'title': title,
                'artist': artist,
                'track_id': track_id,
                'featuring': ''
            }
            title, featuring = self.data_helper.normalise(item['title'], item['artist'])
            item['title_compare'] = title
            item['featuring'] = featuring
            result.append(item)

        self._logger.info('Completed document')
        return result
