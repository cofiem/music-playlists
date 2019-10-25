import json
import logging
import time
from typing import List, Tuple, Optional, Dict

from gmusicapi import Mobileclient

from helper_package.data_helper import DataHelper


class StreamPlaylistGoogleMusic:

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.StreamPlaylistGoogleMusic')
        self._client_mobile = Mobileclient()
        self._data_helper = DataHelper()

    def login(self, device_id: str):
        self._logger.info(f'Logging in to Google Music')
        self._client_mobile.oauth_login(device_id)

    def playlists(self) -> List[Dict]:
        self._logger.info(f'Loading all Google Music playlists')
        return self._client_mobile.get_all_playlists()

    def playlist_update(self, playlist_id: str, name: Optional[str] = None, description: Optional[str] = None,
                        public: Optional[bool] = None) -> str:
        self._logger.info(f'Updating Google Music playlist {playlist_id} ({name})')
        return self._client_mobile.edit_playlist(playlist_id, name, description, public)

    def playlists_songs(self) -> List[Dict]:
        self._logger.info(f'Loading all Google Music playlists with songs')
        return self._client_mobile.get_all_user_playlist_contents()

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

    def search_one(self, query: str, max_results: int = 3) -> List[Dict]:
        self._logger.info(f'Searching Google Music for "{query}"')
        return self._client_mobile.search(query, max_results)

    def query_song(self, title: str, artist: str, featuring: str) -> Tuple[bool, Dict]:
        query = f"{title} {artist} {featuring}".strip()

        # cache response and use cache if available
        key_url = f'gmusicapi {query}'
        result = self._data_helper.cache_load_page(key_url)
        used_cache = False
        if result:
            result = json.loads(result.decode('utf-8'))
            used_cache = True
        else:
            result = self.search_one(query)
            self._data_helper.cache_save_page(key_url, json.dumps(result).encode('utf-8'))

        return used_cache, result

