import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from urllib.parse import urlencode

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader
from music_playlists.music_service.google_music import GoogleMusic
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_service.spotify import Spotify
from music_playlists.music_source.source_playlist import SourcePlaylist


class TripleJMostPlayed:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': 'Double J Most Played Daily',
            'source_url': 'https://www.abc.net.au/doublej/featured-music/most-played/',
            'source_name': 'doublej',
            'services': {
                GoogleMusic.CODE: 'GOOGLE_MUSIC_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED',
                Spotify.CODE: 'SPOTIFY_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED',
            }
        },
        {
            'title': 'Triple J Most Played Daily',
            'source_url': 'https://www.abc.net.au/triplej/featured-music/most-played/',
            'source_name': 'triplej',
            'services': {
                GoogleMusic.CODE: 'GOOGLE_MUSIC_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED',
                Spotify.CODE: 'SPOTIFY_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED',
            }
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader

        # https://music.abcradio.net.au/api/v1/recordings/plays.json?order=desc&limit=50&service=doublej&from=2019-11-12T13:00:00Z&to=2019-11-19T13:00:00Z
        self._url = 'https://music.abcradio.net.au/api/v1/recordings/plays.json?{qs}'
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

        # build dates for urls
        current_time = datetime.now(tz=self._time_zone)
        current_day = current_time.date()

        url = self.build_url(
            data['source_name'], date_from=current_day - timedelta(days=8), date_to=current_day - timedelta(days=1))

        # download track list
        tracks_data = self._downloader.download_json(self._downloader.cache_persisted, url)

        for index, item in enumerate(tracks_data['items']):
            title = item['title']
            track_id = item['arid']
            original_artists = item['artists']

            # get primary artist and featured artists
            artist = ''
            featuring = ''
            for raw_artist in original_artists:
                if raw_artist['type'] == 'primary':
                    artist = f'{artist}, {raw_artist["name"]}'
                elif raw_artist['type'] == 'featured':
                    featuring = f'{artist}, {raw_artist["name"]}'
                else:
                    raise Exception(f"Unrecognised artist {raw_artist['type']}, {artist}, {raw_artist['name']}.")

            artists = [artist.strip(', ')]
            for i in featuring.split(', '):
                featured = i.strip(', ')
                if featured and featured not in artists:
                    artists.append(featured)

            # build track
            source_playlist.tracks.append(Track(
                track_id=track_id,
                name=title,
                artists=artists,
                info={
                    'source_id': track_id,
                    'source_order': index + 1,
                    'original_track': title,
                    'original_artists': original_artists
                }))

        self._logger.info(f"Completed '{data['title']}'")
        return source_playlist, service_playlists

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
