import logging

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_service.google_music import GoogleMusic
from music_playlists.music_service.spotify import Spotify
from music_playlists.music_source.radio4zzz_most_played import Radio4zzzMostPlayed
from music_playlists.music_source.triplej_most_played import TripleJMostPlayed
from music_playlists.music_source.triplej_unearthed_chart import TripleJUnearthedChart


class Process:
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._downloader = Downloader()
        self._time_zone = pytz.timezone('Australia/Brisbane')
        self._gmusic = GoogleMusic(self._downloader, self._time_zone)
        self._spotify = Spotify(self._downloader, self._time_zone)
        self._radio4zzz_most_played = Radio4zzzMostPlayed(self._downloader, self._time_zone)
        self._triplej_most_played = TripleJMostPlayed(self._downloader, self._time_zone)
        self._triplej_unearthed_chart = TripleJUnearthedChart(self._downloader, self._time_zone)

    def run(self):
        self._logger.info('Updating music playlists')

        # obtain the track information and normalise the track details
        playlists = {}
        sources = [
            self._radio4zzz_most_played.playlists(),
            self._triplej_most_played.playlists(),
            self._triplej_unearthed_chart.playlists(),
        ]
        for source in sources:
            for source_playlist, service_playlists in source:
                for service_playlist in service_playlists:
                    if service_playlist.service_name not in playlists:
                        playlists[service_playlist.service_name] = {}
                    if service_playlist.playlist_name in playlists[service_playlist.service_name]:
                        raise Exception("Unexpected duplicate service playlists.")
                    playlists[service_playlist.service_name][service_playlist.playlist_name] = {
                        'source': source_playlist,
                        'service': service_playlist
                    }

        # find songs in streaming services and build new playlists
        self._gmusic.login()
        services = {
            GoogleMusic.CODE: self._gmusic,
        }
        for service_name, service_object in services.items():
            for playlist_name, playlist_object in playlists[service_name].items():
                source_playlist = playlist_object['source']
                service_playlist = playlist_object['service']

                self._logger.info(f"Started updating '{service_name}' playlist "
                                  f"'{service_playlist.playlist_name}' "
                                  f"({service_playlist.service_playlist_code})")
                playlist_existing = service_object.playlist_existing(service_playlist)
                playlist_new = service_object.playlist_new(source_playlist, playlist_existing)
                service_object.playlist_update(playlist_existing, playlist_new)

                self._logger.info(f"Finished updating '{service_name}' playlist "
                                  f"'{playlist_new.playlist_title}' "
                                  f"({playlist_new.service_playlist_code})")

        # done
        self._logger.info('Finished updating music playlists')
