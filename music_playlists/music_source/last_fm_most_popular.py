import logging
from typing import List, Optional
from urllib.parse import urlencode


from music_playlists.downloader import Downloader
from music_playlists.music_source.source_playlist import SourcePlaylist
from music_playlists.track import Track


class LastFmMostPopular(SourcePlaylist):
    code = "lastfm_most_popular"
    title = "Last.fm Most Popular Weekly"

    def __init__(self, logger: logging.Logger, downloader: Downloader, api_key: str):
        self._logger = logger
        self._downloader = downloader
        self._api_key = api_key
        self._url = "https://ws.audioscrobbler.com/2.0/?{qs}"

    def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
        # get content
        url = self.build_url(api_key=self._api_key)

        # download track list
        tracks_data = self._downloader.download_json(url)

        result = []
        for index, item in enumerate(tracks_data["tracks"]["track"]):
            result.append(
                Track.create(
                    self.code,
                    item.get("url"),
                    item["name"],
                    [item["artist"]["name"]],
                    item,
                )
            )

        self._logger.info(f"Retrieved {self.title} with {len(result)} tracks.")
        if limit is not None and 0 < limit < len(result):
            result = result[:limit]
        return result

    def build_url(
        self,
        api_key: str,
        method: str = "geo.gettoptracks",
        country: str = "australia",
        output_format: str = "json",
        limit: bool = "50",
        page: str = "1",
    ):
        qs = urlencode(
            {
                "api_key": api_key,
                "method": method,
                "country": country,
                "format": output_format,
                "limit": limit,
                "page": page,
            }
        )
        url = self._url.format(qs=qs)
        return url
