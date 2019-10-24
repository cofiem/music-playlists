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
        self._client_mobile.oauth_login(device_id)

    def playlists(self) -> List[Dict]:
        return self._client_mobile.get_all_playlists()

    def playlist_update(self, playlist_id: str, name: Optional[str] = None, description: Optional[str] = None,
                        public: Optional[bool] = None) -> str:
        return self._client_mobile.edit_playlist(playlist_id, name, description, public)

    def playlist_songs(self) -> List[Dict]:
        return self._client_mobile.get_all_user_playlist_contents()

    def playlist_songs_add(self, playlist_id: str, song_ids: List[str]) -> List[str]:
        return self._client_mobile.add_songs_to_playlist(playlist_id, song_ids)

    def playlist_songs_remove(self, song_ids: List[str]) -> List[Tuple[str, str]]:
        """
        Remove songs from a playlist. The song ids are the playlist-specific song ids.
        :param song_ids:
        :return:
        """
        return self._client_mobile.remove_entries_from_playlist(song_ids)

    def search_one(self, query: str, max_results: int = 3) -> List[Dict]:
        self._logger.info(f'Searching Google Music for "{query}"')
        return self._client_mobile.search(query, max_results)

    def search_many(self, queries: List[str], max_results: int = 3) -> Dict[str, List[Dict]]:
        result = {}
        for query in queries:
            search_result = self.search_one(query, max_results)
            result[query] = search_result
            # sleep so that the requests to the API aren't too much
            time.sleep(1)
        return result

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

    def select_song(self, song_hits: List[Dict], query_title: str, query_artist: str):
        # if there are songs, then no match
        if len(song_hits) == 0:
            return {}

        # if there are results, then the query title and artist must appear in the result
        for song in song_hits:
            if self._is_match(query_title, query_artist, song['track']['title'], song['track']['artist']):
                return song['track']

        # if there are no matches, then no match
        return {}

    def build_result(self, selected_song: Optional[Dict], query_song: Dict):
        selected_title = selected_song.get('title')
        selected_artist = selected_song.get('artist')

        return {
            'track_id': selected_song.get('id') or selected_song.get('nid') or
                        selected_song.get('storeId') or selected_song.get('trackId'),
            'title': selected_song.get('title'),
            'artist': selected_song.get('artist'),
            'match': self._is_match(query_song['title'], query_song['artist'], selected_title, selected_artist)
        }

    def _is_match(self, query_title: str, query_artist: str, result_title: str, result_artist: str):
        if not query_title or not result_title or not query_artist or not result_artist:
            return False

        q_title = self._data_helper.normalise(query_title, query_artist)
        q_artist = query_artist.lower().strip()
        r_title = self._data_helper.normalise(result_title, result_artist)
        r_artist = result_artist.lower().strip()

        if q_title in r_title and q_artist == r_artist:
            return True

        if q_artist in r_artist and q_title == r_title:
            return True

        return False
