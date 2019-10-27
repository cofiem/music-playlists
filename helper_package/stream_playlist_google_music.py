import logging
import os
from typing import List, Tuple, Optional, Dict

from gmusicapi import Mobileclient

from helper_package.data_helper import DataHelper


class StreamPlaylistGoogleMusic:

    def __init__(self, data_helper: DataHelper = None):
        self._logger = logging.getLogger('music_playlists.StreamPlaylistGoogleMusic')
        self._client_mobile = Mobileclient()
        self._data_helper = data_helper or DataHelper()

    def login(self, device_id: str) -> bool:
        self._logger.info(f'Logging in to Google Music')
        return self._client_mobile.oauth_login(device_id)

    def playlists(self) -> List[Dict]:
        self._logger.info(f'Loading all Google Music playlists')
        return self._client_mobile.get_all_playlists()

    def playlist_update(self, playlist_id: str, name: Optional[str] = None, description: Optional[str] = None,
                        public: Optional[bool] = None) -> str:
        self._logger.info(f'Updating Google Music playlist {playlist_id} ({name})')
        return self._client_mobile.edit_playlist(playlist_id, name, description, public)

    def playlists_songs(self) -> Tuple[bool, List[Dict]]:
        self._logger.info(f'Loading all Google Music playlists with songs')

        key = f'gmusicapi-playlists-with-songs'
        result = self._data_helper.cache_load_object(key)
        used_cache = False
        if result:
            used_cache = True
        else:
            result = self._client_mobile.get_all_user_playlist_contents()
            self._data_helper.cache_save_object(key, result)

        return used_cache, result

    def playlist_songs_add(self, playlist_id: str, song_ids: List[str]) -> List[str]:
        self._logger.info(f'Adding {len(song_ids)} songs to Google Music playlist {playlist_id}')
        return self._client_mobile.add_songs_to_playlist(playlist_id, song_ids)

    def playlist_songs_remove(self, song_ids: List[str]) -> List[Tuple[str, str]]:
        """
        Remove songs from a playlist. The song ids are the playlist-specific song ids.
        :param song_ids:
        :return:
        """
        self._logger.info(f'removing {len(song_ids)} songs from Google Music playlist')
        return self._client_mobile.remove_entries_from_playlist(song_ids)

    def query_song(self, title: str, artist: str, featuring: str, max_results: int = 3) -> Tuple[bool, Dict]:
        q_title, q_artist, q_featuring = self._data_helper.normalise(title, artist, featuring)

        queries = [
            f"{q_title} - {q_artist} {q_featuring}".strip(),
            f"{q_title} - {q_artist}".strip()
        ]

        used_cache = False
        result = {}
        for query in queries:
            self._logger.info(f'Searching Google Music for "{query}"')

            # cache response and use cache if available
            key = f'gmusicapi-query-{query}'
            result = self._data_helper.cache_load_object(key)
            used_cache = False
            if result:
                used_cache = True
            else:
                result = self._client_mobile.search(query, max_results)
                self._data_helper.cache_save_object(key, result)

            if result and result['song_hits']:
                # stop if there are results
                break

        return used_cache, result

    def playlists_update(self, playlists: List) -> List[Dict]:
        # get all gmusic playlists with songs
        gmusic_used_cache, gmusic_playlists = self.playlists_songs()

        result = []

        # update the google music playlists
        for playlist in playlists:
            song_ids_old = []
            for gmusic_playlist in gmusic_playlists:
                if gmusic_playlist['id'] == playlist['id']:
                    for t in gmusic_playlist.get('tracks', []):
                        if not t.get('track'):
                            continue
                        song_playlist_id = t['id']
                        song_track_id = t['track'].get('storeId') or t['track'].get('trackId') or \
                                        t['track'].get('id') or t['track'].get('nid')
                        song_ids_old.append((song_playlist_id, song_track_id))

            playlist_id = playlist['id']
            playlist_name = playlist['name']
            playlist_description = playlist['description']
            song_ids_new = playlist['song_ids_new']

            # rename existing playlist
            self.playlist_update(playlist_id, playlist_name, playlist_description, public=True)

            # remove all old songs, then add all new songs, to keep order of songs
            song_playlist_ids_to_remove = [i[0] for i in song_ids_old]
            if song_playlist_ids_to_remove:
                self.playlist_songs_remove(song_playlist_ids_to_remove)

            # add new set of songs
            if song_ids_new:
                self.playlist_songs_add(playlist_id, song_ids_new)

            result.append({
                'songs_removed_count': len(song_playlist_ids_to_remove),
                'songs_added_count': len(song_ids_new),
                'playlist_id': playlist_id,
                'playlist_name': playlist_name
            })
        return result

    def gmusic_login(self):
        gmusicapi_creds_data = os.getenv('GMUSIC_COFIG')
        device_id = os.getenv('GMUSICAPI_DEVICE_ID')

        if gmusicapi_creds_data:
            gmusicapi_creds_dir = '/home/circleci/.local/share/gmusicapi'
            gmusicapi_creds_file = 'mobileclient.cred'

            os.makedirs(gmusicapi_creds_dir, exist_ok=True)
            with open(os.path.join(gmusicapi_creds_dir, gmusicapi_creds_file), 'wt') as creds_f:
                creds_f.write(gmusicapi_creds_data)

        return self.login(device_id)
