import logging
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict

from gmusicapi import Mobileclient

from music_playlists.data.track import Track
from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_source.source_playlist import SourcePlaylist


class GoogleMusic:
    _logger = logging.getLogger(__name__)
    CODE = 'gmusic'

    def __init__(self, downloader: Downloader, time_zone):
        self._time_zone = time_zone
        self._client_mobile = Mobileclient(debug_logging=False)
        self._downloader = downloader
        self._gmusic_playlists = None

    def login(self) -> bool:
        """Login to google music."""
        self._logger.info(f'Logging in to Google Music')
        creds_data = os.getenv('GOOGLE_MUSIC_AUTH_CONFIG')
        device_id = os.getenv('GOOGLE_MUSIC_AUTH_DEVICE_ID')

        if not creds_data or not device_id:
            raise Exception("Could not obtain 'GOOGLE_MUSIC_AUTH_CONFIG' or 'GOOGLE_MUSIC_AUTH_DEVICE_ID'")

        # create creds file
        if os.getenv('CI'):
            creds_path = Path('/home/circleci/.local/share/gmusicapi/mobileclient.cred')
        else:
            creds_path = Path(Path.home(), 'mobileclient.cred')

        if not creds_path.exists():
            self._logger.info("Writing Google Music login creds file")
            creds_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(creds_path), 'wt') as f:
                f.write(creds_data)

        # login
        login_result = self._client_mobile.oauth_login(device_id, str(creds_path))

        if login_result is not True:
            raise Exception("Could not login to Google Music.")

        return login_result

    def playlists(self) -> List[Dict]:
        """Load all playlist metadata."""
        self._logger.info(f'Loading all Google Music playlists')
        return self._client_mobile.get_all_playlists()

    def playlist_update_metadata(self, playlist_id: str, title: Optional[str] = None, description: Optional[str] = None,
                                 public: Optional[bool] = None) -> str:
        """Update playlist metadata."""
        self._logger.info(f"Updating Google Music playlist details")
        return self._client_mobile.edit_playlist(playlist_id, title, description, public)

    def playlists_songs(self) -> List[Dict]:
        """Load all playlists with their track listings."""
        if self._gmusic_playlists is None:
            self._logger.info(f'Retrieving all Google Music playlists with songs')
            self._gmusic_playlists = self._client_mobile.get_all_user_playlist_contents()
        else:
            self._logger.info(f'Loading from cache all Google Music playlists with songs')
        return self._gmusic_playlists

    def playlist_songs_add(self, playlist_id: str, song_ids: List[str]) -> List[str]:
        """Add songs to a playlist. The song ids are the general track ids."""
        self._logger.info(f"Adding {len(song_ids)} songs")
        # TODO: this fails with TOO_MANY_ITEMS error
        return self._client_mobile.add_songs_to_playlist(playlist_id, song_ids)

    def playlist_songs_remove(self, song_ids: List[str]) -> List[Tuple[str, str]]:
        """Remove songs from a playlist. The song ids are the playlist-specific song ids."""
        self._logger.info(f"Removing {len(song_ids)} songs")
        return self._client_mobile.remove_entries_from_playlist(song_ids)

    def playlist_existing(self, service_playlist: ServicePlaylist) -> ServicePlaylist:
        playlist_tracks = self.playlists_songs()
        result = ServicePlaylist(
            playlist_name=service_playlist.playlist_name,
            service_name=service_playlist.service_name,
            service_playlist_env_var=service_playlist.service_playlist_env_var,
            service_playlist_code=service_playlist.service_playlist_code
        )
        for gmusic_playlist in playlist_tracks:
            if gmusic_playlist['id'] == service_playlist.service_playlist_code:
                for t in gmusic_playlist.get('tracks', []):
                    if not t.get('track'):
                        continue
                    result.tracks.append(Track(
                        track_id=self._get_track_id(t),
                        name=t['track'].get('title'),
                        artists=[t['track'].get('artist')],
                        info=t))
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

    def playlist_update(self, service_playlist_old: ServicePlaylist, service_playlist_new: ServicePlaylist) -> None:
        self.playlist_update_metadata(
            playlist_id=service_playlist_new.service_playlist_code,
            title=service_playlist_new.playlist_title,
            description=service_playlist_new.playlist_description,
            public=True)

        # remove all old songs, then add all new songs, to keep order of songs
        song_playlist_ids_to_remove = [i.info.get('track_playlist_id') for i in service_playlist_old.tracks]
        if song_playlist_ids_to_remove:
            self.playlist_songs_remove(song_playlist_ids_to_remove)

        # add new set of songs
        song_playlist_ids_to_add = []
        for track in service_playlist_new.tracks:
            if track.track_id and track.track_id not in song_playlist_ids_to_add:
                song_playlist_ids_to_add.append(track.track_id)
        if song_playlist_ids_to_add:
            self.playlist_songs_add(service_playlist_new.service_playlist_code, song_playlist_ids_to_add)

    def _query_song(self, item: 'Track', max_results: int = 3) -> Tuple[bool, List['Track']]:
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
                self._logger.info(f"Searching Google Music for '{query}'")
                query_result = self._client_mobile.search(query, max_results)
                self._downloader.store_object(self._downloader.cache_persisted, key, query_result)

            # stop if there are results
            if query_result and query_result.get('song_hits'):
                for song_hit in query_result['song_hits']:
                    match = song_hit.get('track')
                    if not match:
                        continue
                    track = Track(
                        track_id=self._get_track_id(match),
                        name=match.get('title'),
                        artists=[match.get('artist')],
                        info={**match}
                    )

                    self._logger.debug(f"Found match for '{query}' on Google Music: {str(track)}")
                    tracks.append(track)
                    break
        return used_cache, tracks

    def _get_track_id(self, track: Dict) -> Optional[str]:
        """Get the track_id for a Google Music track."""
        track_id = track.get('storeId') or track.get('id') or track.get('trackId') or track.get('nid')
        if track.get('track'):
            track_data = track.get('track')
            track_id = track_id or track_data.get('storeId') or track_data.get('id') or track_data.get(
                'trackId') or track_data.get('nid')
        return track_id
