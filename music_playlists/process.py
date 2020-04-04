import logging
import os

from music_playlists.downloader import Downloader
from music_playlists.music_source.radio4zzz_most_played import Radio4zzzMostPlayed
from music_playlists.music_source.triplej_most_played import TripleJMostPlayed
from music_playlists.music_source.triplej_unearthed_chart import TripleJUnearthedChart
from music_playlists.playlist_data import PlaylistData
from music_playlists.stream_playlist.google_music import GoogleMusic
from music_playlists.stream_playlist.spotify import Spotify


class Process:
    _logger = logging.getLogger(__name__)

    def __init__(self):
        is_ci = os.getenv('CI') == 'true'
        self._downloader = Downloader(use_cache=not is_ci)
        self._playlist_data = PlaylistData()
        self._gmusic = GoogleMusic(self._downloader, self._playlist_data)
        self._spotify = Spotify(self._downloader, self._playlist_data)

    def run(self):
        self._logger.info('Updating music playlists')
        radio4zzz_most_played = Radio4zzzMostPlayed(self._downloader)
        triplej_most_played = TripleJMostPlayed(self._downloader)
        triplej_unearthed_chart = TripleJUnearthedChart(self._downloader)

        # obtain the track information and normalise the track details
        tracks = []
        for available_items in triplej_most_played.available:
            tracks.extend(triplej_most_played.run(available_items))

        for available_items in triplej_unearthed_chart.available:
            tracks.extend(triplej_unearthed_chart.run(available_items))

        for available_items in radio4zzz_most_played.available:
            tracks.extend(radio4zzz_most_played.run(available_items))

        replacements = [
            {'match_artist': 'thelma plum', 'match_track': 'better in black',
             'replace_artist': 'thelma plum', 'replace_track': 'better in blak'},
            {'match_artist': 'zac eichner', 'match_track': 'lucy   live at jive',
             'replace_artist': 'zac eichner', 'replace_track': 'lucy'},
        ]

        # normalise the tracks
        for track in tracks:
            new_track, new_artist, new_featuring = self._playlist_data.normalise(
                track['track'], track['artist'], track['featuring'])
            track['track_normalised'] = new_track
            track['artist_normalised'] = new_artist
            track['featuring_normalised'] = new_featuring

            for replacement in replacements:
                if replacement['match_track'] == track['track_normalised'] and \
                        replacement['match_artist'] == track['artist_normalised']:
                    track['track_normalised'] = replacement['replace_track']
                    track['artist_normalised'] = replacement['replace_artist']

        # find songs in streaming services
        self._gmusic.login()
        self._gmusic.query_songs(tracks)

        self._spotify.query_songs(tracks)

        # build playlists
        playlists = self._playlist_data.build_playlists(tracks)

        # update stream service playlists
        self._gmusic.playlists_update(playlists)
        self._spotify.playlists_update(playlists)

        # done
        self._logger.info('Finished updating music playlists')
