import logging
from typing import List, Optional

from lxml import html


from music_playlists.downloader import Downloader
from music_playlists.music_source.source_playlist import SourcePlaylist
from music_playlists.track import Track


class TripleJUnearthedChart(SourcePlaylist):
    code = "triple_j_unearthed_chart"
    title = "Triple J Unearthed Weekly"

    def __init__(self, logger: logging.Logger, downloader: Downloader):
        self._logger = logger
        self._downloader = downloader
        self._url = "https://www.triplejunearthed.com/discover/charts"

    def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
        self._logger.info(f"Started {self.title}.")

        cache_name = self._downloader.cache_temp
        content_text = self._downloader.download_text(cache_name, self._url)
        content_html = html.fromstring(content_text)

        result = []
        for row in content_html.xpath('//li[@class="track"]'):
            order = row.xpath('./div[@class="this_week"]/text()')[0].strip()
            title = row.xpath('./div[@class="track_title"]/text()')[0].strip()
            artist = row.xpath('./div[@class="artist"]/a/@title')[0].strip()

            track_id_xpath = (
                './div[@class="play_actions"]/a[@class="play_download_large"]/@href'
            )
            track_id = (
                row.xpath(track_id_xpath)[0].strip().replace("/download/track/", "")
            )

            result.append(
                Track.create(
                    self.code,
                    track_id,
                    title,
                    [artist],
                    {
                        "title": title,
                        "artist": artist,
                        "source_id": track_id,
                        "source_order": order,
                    },
                )
            )

        self._logger.info(f"Completed {self.title} with {len(result)} tracks.")
        if limit is not None and 0 < limit < len(result):
            result = result[:limit]
        return result
