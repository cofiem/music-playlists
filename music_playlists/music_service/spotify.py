import base64
import logging
import os
import secrets
import webbrowser
from typing import Tuple, List, Optional
from urllib.parse import urlencode

import requests

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_source.source_playlist import SourcePlaylist


class Spotify:
    _logger = logging.getLogger(__name__)
    CODE = 'spotify'

    def __init__(self, downloader: Downloader, time_zone):
        self._time_zone = time_zone
        self._downloader = downloader
        self._access_token = None

    def login(self) -> bool:
        """Login to spotify."""
        refresh_token = os.getenv('SPOTIFY_AUTH_REFRESH_TOKEN')
        client_id = os.getenv('SPOTIFY_AUTH_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_AUTH_CLIENT_SECRET')

        if not refresh_token or not client_id or not client_secret:
            raise Exception("Could not obtain 'SPOTIFY_AUTH_REFRESH_TOKEN' or "
                            "'SPOTIFY_AUTH_CLIENT_ID' or 'SPOTIFY_AUTH_CLIENT_SECRET'.")

        self._access_token = self._login_token_next(client_id, client_secret, refresh_token)
        return True

    def playlist_existing(self, service_playlist: ServicePlaylist) -> ServicePlaylist:
        playlist_tracks = self.playlist_songs(service_playlist.service_playlist_code)
        result = ServicePlaylist(
            playlist_name=service_playlist.playlist_name,
            service_name=service_playlist.service_name,
            service_playlist_env_var=service_playlist.service_playlist_env_var,
            service_playlist_code=service_playlist.service_playlist_code
        )
        for track in playlist_tracks['items']:
            result.tracks.append(Track(
                track_id=track['track'].get('id'),
                name=track['track'].get('name'),
                artists=[artist.get('name') for artist in track['track'].get('artists')],
                info=track))
        return result

    def playlist_new(self, source_playlist: SourcePlaylist, service_playlist: ServicePlaylist) -> ServicePlaylist:
        result = ServicePlaylist(
            playlist_name=service_playlist.playlist_name,
            service_name=service_playlist.service_name,
            service_playlist_env_var=service_playlist.service_playlist_env_var,
            service_playlist_code=service_playlist.service_playlist_code
        )

        result.populate_tracks(source_playlist.tracks, service_playlist.tracks, self._query_song, self._time_zone)

        return result

    def playlist_update(self, service_playlist_old: ServicePlaylist, service_playlist_new: ServicePlaylist):
        # update playlist metadata
        self.playlist_update_metadata(
            playlist_id=service_playlist_new.service_playlist_code,
            title=service_playlist_new.playlist_title,
            description=service_playlist_new.playlist_description,
            public=True)

        # add new set of songs
        song_playlist_ids_to_add = []
        for track in service_playlist_new.tracks:
            track_id = track.info.get('id')
            if track_id and track_id not in song_playlist_ids_to_add:
                song_playlist_ids_to_add.append(track_id)
        if song_playlist_ids_to_add:
            self.playlist_songs_set(service_playlist_new.service_playlist_code, song_playlist_ids_to_add)

    def playlist_update_metadata(self, playlist_id: str, title: Optional[str] = None, description: Optional[str] = None,
                                 public: Optional[bool] = None) -> bool:
        """Update playlist metadata."""
        self._logger.info(f"Updating Spotify playlist details")

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        data = {
            'name': title,
            'description': description,
            'public': 'true' if public else 'false'
        }
        headers = {
            'Authorization': f"Bearer {self._access_token}"
        }
        r = requests.get(url, json=data, headers=headers)
        return r.status_code == requests.codes.ok

    def playlist_songs(self, playlist_id: str):
        """Get the tracks in a playlist."""
        self._logger.info("Getting Spotify playlist songs")
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {
            'fields': 'items(track(name,id,artists(name)))',
            'market': 'AU',
            'limit': 100,
            'offset': 0
        }
        headers = {
            'Authorization': f"Bearer {self._access_token}",
        }
        r = requests.get(url, params=params, headers=headers)
        content = r.json()
        return content

    def playlist_songs_set(self, playlist_id: str, song_ids: List[str]) -> List[str]:
        """Replace songs in a playlist."""
        self._logger.info(f"Adding {len(song_ids)} songs")
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {
            'uris': [f"spotify:track:{song_id}" for song_id in song_ids]
        }
        headers = {
            'Authorization': f"Bearer {self._access_token}",
        }
        r = requests.put(url, json=params, headers=headers)
        content = r.json()
        return content

    def login_init(self):
        client_id = os.getenv('SPOTIFY_AUTH_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_AUTH_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise Exception("Could not obtain 'SPOTIFY_AUTH_CLIENT_ID' or 'SPOTIFY_AUTH_CLIENT_SECRET'.")

        request_state = secrets.token_hex(10)
        redirect_uri = 'https://www.anotherbyte.net/callback'

        self._login_authorise(client_id, redirect_uri, request_state)
        auth_code = input("Enter the 'code' from the authorisation url:")

        access_token, refresh_token = self._login_token_first(client_id, client_secret, auth_code, redirect_uri)
        print(f"access_token: {access_token}; refresh_token: {refresh_token}")
        return True

    def _login_authorise(self, client_id: str, redirect_uri: str, request_state: str) -> None:
        """Get the url to obtain the Authorization Code."""
        qs = urlencode({
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'playlist-modify-public',
            'state': request_state
        })
        url = 'https://accounts.spotify.com/authorize?{qs}'.format(qs=qs)
        webbrowser.open(url, new=2)

    def _login_token_first(self, client_id: str, client_secret: str, auth_code: str,
                           redirect_uri: str) -> Tuple[str, str]:
        """Get the initial access token and refresh token."""
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
        }
        headers = {
            'Authorization': f"Basic {self._login_client_auth(client_id, client_secret)}",
        }
        r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
        if r.status_code == requests.codes.ok:
            response = r.json()
            access_token = response.get('access_token')
            refresh_token = response.get('refresh_token')
            return access_token, refresh_token
        else:
            raise Exception(f"Could not get access and refresh token Spotify, got http code {r.status_code}.")

    def _login_token_next(self, client_id: str, client_secret: str, refresh_token: str):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        headers = {
            'Authorization': f"Basic {self._login_client_auth(client_id, client_secret)}",
        }
        r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
        if r.status_code == requests.codes.ok:
            response = r.json()
            access_token = response.get('access_token')
            return access_token
        else:
            raise Exception(f"Could not get refresh Spotify access token, got http code {r.status_code}.")

    def _login_client_auth(self, client_id: str, client_secret: str):
        basic = f"{client_id}:{client_secret}"
        basic_b64 = base64.b64encode(basic.encode())
        return basic_b64.decode()

    def _query_song(self, item: 'Track', max_results: int = 2) -> Tuple[bool, List['Track']]:
        self._logger.debug(f"Searching Google Music for match to '{str(item)}'")

        queries = item.query_strings
        used_cache = False
        tracks = []
        for query in queries:
            # cache response and use cache if available
            key = f"{self.CODE}api query {query}"
            query_result = self._downloader.retrieve_object(self._downloader.cache_persisted, key)
            if query_result is not None:
                used_cache = True
                query_result = query_result.get_value()
            else:
                self._logger.info(f"Searching Spotify for '{query}'")
                url = f"https://api.spotify.com/v1/search"
                params = {
                    'q': query,
                    'limit': max_results,
                    'offset': 0,
                    'type': 'track',
                    'market': 'AU'
                }
                headers = {
                    'Authorization': f"Bearer {self._access_token}",
                }
                r = requests.get(url, params=params, headers=headers)
                query_result = r.json()
                self._downloader.store_object(self._downloader.cache_persisted, key, query_result)

            # stop if there are results
            if query_result and query_result['tracks'].get('items'):
                for song_hit in query_result['tracks'].get('items'):
                    track = Track(
                        track_id=song_hit.get('id'),
                        name=song_hit.get('name'),
                        artists=[artist.get('name') for artist in song_hit.get('artists')],
                        info=song_hit
                    )

                    self._logger.debug(f"Found match for '{query}' on Google Music: {str(track)}")
                    tracks.append(track)
                    break
        return used_cache, tracks
