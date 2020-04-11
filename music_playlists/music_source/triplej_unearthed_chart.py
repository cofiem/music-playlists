import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

from lxml import html

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader
from music_playlists.music_service.google_music import GoogleMusic
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_source.source_playlist import SourcePlaylist


class TripleJUnearthedChart:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'Triple J Unearthed Weekly',
            'services': {
                GoogleMusic.CODE: 'GOOGLE_MUSIC_PLAYLIST_TRIPLEJ_UNEARTHED_ID',
            }
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader
        self._url = 'https://www.triplejunearthed.com/discover/charts'
        self._time_zone = time_zone

    def playlists(self):
        result = []
        for item in self.available:
            result.append(self.playlist(item))
        return result

    def playlist(self, data: Dict[str, Any]) -> Tuple[SourcePlaylist, List[ServicePlaylist]]:
        self._logger.info(f"Started '{data['title']}'")

        # create source playlist and service playlists
        source_playlist = SourcePlaylist(playlist_name=data['title'])
        service_playlists = []
        for k, v in data['services'].items():
            service_playlists.append(ServicePlaylist(
                playlist_name=data['title'],
                service_name=k,
                service_playlist_env_var=v))

        content_text = self._downloader.download_text(self._downloader.cache_temp, self._url)
        content_html = html.fromstring(content_text)

        for row in content_html.xpath('//li[@class="track"]'):
            order = row.xpath('./div[@class="this_week"]/text()')[0].strip()
            title = row.xpath('./div[@class="track_title"]/text()')[0].strip()
            artist = row.xpath('./div[@class="artist"]/a/@title')[0].strip()

            track_id_xpath = './div[@class="play_actions"]/a[@class="play_download_large"]/@href'
            track_id = row.xpath(track_id_xpath)[0].strip().replace('/download/track/', '')

            source_playlist.tracks.append(Track(
                name=title,
                artists=[artist],
                info={
                    'source_id': track_id,
                    'source_order': order
                }
            ))

        self._logger.info(f"Completed {data['title']}")
        return source_playlist, service_playlists
