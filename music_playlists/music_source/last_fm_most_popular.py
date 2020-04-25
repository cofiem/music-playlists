import logging
import os
from datetime import datetime
from typing import Any, List, Dict, Tuple
from urllib.parse import urlencode

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader
from music_playlists.music_service.google_music import GoogleMusic
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_service.spotify import Spotify
from music_playlists.music_source.source_playlist import SourcePlaylist


class LastFmMostPopular:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'Last.fm Most Popular Weekly',
            'source_url': 'https://www.last.fm/charts',
            'services': {
                GoogleMusic.CODE: 'GOOGLE_MUSIC_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS',
                Spotify.CODE: 'SPOTIFY_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS',
            }
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader
        self._time_zone = time_zone

        self._url = 'https://ws.audioscrobbler.com/2.0/?{qs}'

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

        # get content
        api_key = os.getenv('LASTFM_AUTH_API_KEY')
        url = self.build_url(api_key=api_key)

        # download track list
        tracks_data = self._downloader.download_json(self._downloader.cache_temp, url)

        for index, item in enumerate(tracks_data['tracks']['track']):
            source_playlist.tracks.append(Track(
                track_id=item.get('url'),
                name=item['name'],
                artists=[item['artist']['name']],
                info=item))

        self._logger.info(f"Completed '{data['title']}'")
        return source_playlist, service_playlists

    def build_url(self, api_key: str,
                  method: str = 'geo.gettoptracks',
                  country: str = 'australia',
                  format: str = 'json',
                  limit: bool = '50',
                  page: str = '1'
                  ):
        qs = urlencode({
            'api_key': api_key,
            'method': method,
            'country': country,
            'format': format,
            'limit': limit,
            'page': page,
        })
        url = self._url.format(qs=qs)
        return url
