import json
from typing import List, Tuple, Dict
from unittest import TestCase

import pytz

from music_playlists.data.track import Track
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_source.source_playlist import SourcePlaylist


class TestServicePlaylist(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._time_zone = pytz.timezone('Australia/Brisbane')

    def test_populate_tracks(self):
        with open('service_playlists.json') as f:
            service_playlists = json.load(f)
        with open('source_playlists.json') as f:
            source_playlists = json.load(f)

        for index in range(len(service_playlists)):
            service_playlist = self._build_service_playlist(service_playlists[index])
            source_playlist = self._build_source_playlist(source_playlists[index])
            result = ServicePlaylist(
                playlist_name=service_playlist.playlist_name,
                service_name=service_playlist.service_name,
                service_playlist_env_var=service_playlist.service_playlist_env_var,
                service_playlist_code=service_playlist.service_playlist_code
            )

            result.populate_tracks(source_playlist.tracks, service_playlist.tracks, self._query_song, self._time_zone)

            return result

    def _query_song(self, item: 'Track', max_results: int = 3) -> Tuple[bool, List['Track']]:
        used_cache = True
        available_tracks = [item]
        return used_cache, available_tracks

    def _build_source_playlist(self, data: Dict) -> SourcePlaylist:
        playlist = SourcePlaylist(
            playlist_name=data['playlistName']
        )
        for track in data['tracks']:
            playlist.tracks.append(self._build_track(track))
        return playlist

    def _build_service_playlist(self, data: Dict) -> ServicePlaylist:
        playlist = ServicePlaylist(
            playlist_name=data['playlistName'],
            service_name=data['serviceName'],
            service_playlist_env_var=data['servicePlaylistEnvVar'],
            service_playlist_code=data['servicePlaylistCode']
        )
        for track in data['tracks']:
            playlist.tracks.append(self._build_track(track))
        return playlist

    def _build_track(self, data: Dict) -> Track:
        return Track(track_id=data['trackId'],
                     name=data['name'],
                     artists=data['artists'],
                     info=data['info'])
