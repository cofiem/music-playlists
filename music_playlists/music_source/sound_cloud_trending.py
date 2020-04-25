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


class SoundCloudTrending:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'SoundCloud Trending Australia Weekly',
            'source_url': 'https://soundcloud.com/charts/new?genre=all-music&country=AU',
            'services': {
                GoogleMusic.CODE: 'GOOGLE_MUSIC_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS',
                Spotify.CODE: 'SPOTIFY_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS',
            }
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader
        self._time_zone = time_zone

        self._url = 'https://api-v2.soundcloud.com/charts?{qs}'

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
        client_id = os.getenv('SOUNDCLOUD_CLIENT_ID')
        url = self.build_url(client_id=client_id)

        # download track list
        tracks_data = self._downloader.download_json(self._downloader.cache_temp, url)

        for index, item in enumerate(tracks_data['collection']):
            track_title = item['track']['title']
            publisher_metadata = item['track'].get('publisher_metadata')
            if publisher_metadata and publisher_metadata.get('artist'):
                artist = publisher_metadata.get('artist')
            elif '-' in track_title:
                track_title_split = track_title.split('-')
                artist = track_title_split[-1]
                track_title = ' '.join(track_title_split[0:-1])
            elif item['track']['user']['full_name']:
                artist = item['track']['user']['full_name']
            elif item['track']['user']['username']:
                artist = item['track']['user']['username']
            else:
                artist = ''

            source_playlist.tracks.append(Track(
                track_id=item['track'].get('id'),
                name=track_title.strip(),
                artists=[artist.strip()],
                info=item))

        self._logger.info(f"Completed '{data['title']}'")
        return source_playlist, service_playlists

    def build_url(self, client_id: str,
                  kind: str = 'trending',
                  genre: str = 'soundcloud:genres:all-music',
                  region: str = 'soundcloud:regions:AU',
                  high_tier_only: bool = False,
                  limit: str = '50',
                  offset: str = '0',
                  linked_partitioning: str = '1',
                  app_locale: str = "en"
                  ):
        qs = urlencode({
            'client_id': client_id,
            'kind': kind,
            'genre': genre,
            'region': region,
            'high_tier_only': str(high_tier_only).lower(),
            'limit': limit,
            'offset': offset,
            'linked_partitioning': linked_partitioning,
            'app_locale': app_locale,
        })
        url = self._url.format(qs=qs)
        return url
