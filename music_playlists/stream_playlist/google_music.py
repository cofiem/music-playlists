import logging
import os
from pathlib import Path
from time import sleep
from typing import List, Tuple, Optional, Dict, Any

from gmusicapi import Mobileclient

from music_playlists.downloader import Downloader
from music_playlists.playlist_data import PlaylistData


class GoogleMusic:
    _logger = logging.getLogger(__name__)

    def __init__(self, downloader: Downloader, playlist_data: PlaylistData):
        self._client_mobile = Mobileclient()
        self._downloader = downloader
        self._playlist_data = playlist_data

    def login(self) -> bool:
        self._logger.info(f'Logging in to Google Music')
        creds_data = os.getenv('GMUSIC_COFIG')
        device_id = os.getenv('GMUSICAPI_DEVICE_ID')

        if not creds_data or not device_id:
            raise Exception("Could not obtain 'GMUSIC_COFIG' or 'GMUSICAPI_DEVICE_ID'")

        # login
        creds_path = Path('/home/circleci/.local/share/gmusicapi/mobileclient.cred') \
            if os.getenv('CI') else Path(Path.home(), 'mobileclient.cred')
        self.write_creds(creds_path, creds_data)
        login_result = self._client_mobile.oauth_login(device_id, str(creds_path))

        # To get the playlist ids
        # gmusic_playlists = self.playlists()

        return login_result

    def playlists(self) -> List[Dict]:
        self._logger.info(f'Loading all Google Music playlists')
        return self._client_mobile.get_all_playlists()

    def playlist_update(self, playlist_id: str, name: Optional[str] = None, description: Optional[str] = None,
                        public: Optional[bool] = None) -> str:
        self._logger.info(f"Updating Google Music playlist details")
        return self._client_mobile.edit_playlist(playlist_id, name, description, public)

    def playlists_songs(self) -> List[Dict]:
        self._logger.info(f'Loading all Google Music playlists with songs')

        key = f'gmusicapi-playlists-with-songs'
        result = self._downloader.cache_load_object(key)
        if result is not None:
            return result.get_value()
        else:
            result = self._client_mobile.get_all_user_playlist_contents()
            self._downloader.cache_save_object(key, result)
            return result

    def playlist_songs_add(self, playlist_id: str, song_ids: List[str]) -> List[str]:
        self._logger.info(f"Adding {len(song_ids)} songs")
        return self._client_mobile.add_songs_to_playlist(playlist_id, song_ids)

    def playlist_songs_remove(self, song_ids: List[str]) -> List[Tuple[str, str]]:
        """Remove songs from a playlist. The song ids are the playlist-specific song ids."""
        self._logger.info(f"Removing {len(song_ids)} songs")
        return self._client_mobile.remove_entries_from_playlist(song_ids)

    def query_song(self, q_title: str, q_artist: str, q_featuring: str, max_results: int = 3) -> Tuple[bool, Dict]:
        queries = [
            f"{q_title} - {q_artist} {q_featuring}".strip(),
            f"{q_title} - {q_artist}".strip()
        ]

        result = {}
        used_cache = False
        for query in queries:
            self._logger.debug(f'Searching Google Music for "{query}"')
            used_cache = False

            # cache response and use cache if available
            key = f'gmusicapi-query-{query}'
            result = self._downloader.cache_load_object(key)
            if result is not None:
                used_cache = True
                result = result.get_value()
            else:
                result = self._client_mobile.search(query, max_results)
                self._downloader.cache_save_object(key, result)

            if result and result['song_hits']:
                # stop if there are results
                match_options = [f"{i['track']['title']} - {i['track']['artist']}" for i in result.get('song_hits')]
                self._logger.debug(f"Found match for '{query}' on Google Music: {match_options}")
                break

        return used_cache, result

    def playlists_update(self, playlists: List[Dict[str, Any]]) -> None:
        self._logger.info(f"Updating Google Music playlists")
        # get all gmusic playlists with songs
        gmusic_playlists = self.playlists_songs()

        # update the google music playlists
        for playlist in playlists:
            if playlist.get('service') != 'gmusic':
                continue

            playlist_id = playlist['playlist_id']
            playlist_name = playlist['display_name']
            playlist_description = playlist['description']
            song_ids_new = playlist['tracks']

            self._logger.info(f"Updating Google Music playlist '{playlist_name}' ({playlist_id})")

            song_ids_old = []
            for gmusic_playlist in gmusic_playlists:
                if gmusic_playlist['id'] == playlist_id:
                    for t in gmusic_playlist.get('tracks', []):
                        if not t.get('track'):
                            continue
                        song_playlist_id = t['id']
                        song_track_id = t['track'].get('storeId') or t['track'].get('trackId') or \
                                        t['track'].get('id') or t['track'].get('nid')
                        song_ids_old.append((song_playlist_id, song_track_id))

            # rename existing playlist
            self.playlist_update(playlist_id, playlist_name, playlist_description, public=True)

            # remove all old songs, then add all new songs, to keep order of songs
            song_playlist_ids_to_remove = [i[0] for i in song_ids_old]
            if song_playlist_ids_to_remove:
                self.playlist_songs_remove(song_playlist_ids_to_remove)

            # add new set of songs
            if song_ids_new:
                self.playlist_songs_add(playlist_id, song_ids_new)

            self._logger.info(f"Finished updating Google Music playlist '{playlist_name}' ({playlist_id})")

        self._logger.info(f"Finished updating Google Music playlists")

    def write_creds(self, creds_path: Path, data) -> None:
        if not creds_path.exists():
            self._logger.info("Writing Google Music login creds file")
            creds_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(creds_path), 'wt') as f:
                f.write(data)

    def query_songs(self, data: List[Dict]) -> None:
        self._logger.info(f'Searching for songs in Google Music')
        for item in data:
            track = item['track_normalised']
            artist = item['artist_normalised']
            featuring = item['featuring_normalised']

            used_cache, gmusic_result = self.query_song(track, artist, featuring)

            hits = gmusic_result['song_hits']
            item['services']['gmusic'] = self._playlist_data.select_song(hits, track, artist, featuring)
            item['services']['gmusic']['playlist_id'] = item['playlist'].get('gmusic_playlist_id')

            if not used_cache:
                sleep(1)

        self._logger.info(f'Done searching Google Music')
