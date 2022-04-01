import logging
from datetime import datetime
from pathlib import Path

import pytz

from music_playlists.abc_radio.manage import Manage as AbcRadioManage
from music_playlists.downloader import Downloader
from music_playlists.intermediate.track import Track
from music_playlists.intermediate.track_list import TrackList
from music_playlists.last_fm.manage import Manage as LastFmManage
from music_playlists.radio_4zzz.manage import Manage as Radio4zzzManage
from music_playlists.settings import Settings
from music_playlists.spotify.client import Client as SpotifyClient
from music_playlists.spotify.manage import Manage as SpotifyManage
from music_playlists.youtube_music.client import Client as YouTubeMusicClient
from music_playlists.youtube_music.manage import Manage as YouTubeMusicManage
from music_playlists.intermediate.manage import Manage as IntermediateManage


class Process:
    _logger = logging.getLogger("music-playlists")

    def __init__(self):
        self._settings = Settings()
        s = self._settings

        self._base_path = Path(s.base_path)
        self._time_zone = pytz.timezone(s.time_zone)
        tz = self._time_zone

        self._downloader = Downloader(self._base_path)
        d = self._downloader

        self._abc_radio = AbcRadioManage(d, tz)
        self._last_fm = LastFmManage(d, tz, s.lastfm_api_key)
        self._radio_4zzz = Radio4zzzManage(d, tz)
        self._spotify_client = SpotifyClient(
            d,
            s.spotify_redirect_uri,
            s.spotify_client_id,
            s.spotify_client_secret,
            s.spotify_refresh_token,
        )
        self._spotify = SpotifyManage(d, self._spotify_client)

        self._youtube_music_client = YouTubeMusicClient(d, s.youtube_music_config)
        self._youtube_music = YouTubeMusicManage(d, self._youtube_music_client)

        self._intermediate = IntermediateManage()

    def run(self):
        self._logger.info("Updating music playlists.")

        self._spotify.client.login()
        self._youtube_music.client.login()

        s = self._settings

        # get the new tracks from the source playlists
        # and find the new tracks in the streaming services
        triplej = self._abc_radio.triplej_most_played()
        self._update_spotify(triplej, s.playlist_spotify_triplej_most_played)
        self._update_youtube_music(
            triplej, s.playlist_youtube_music_triplej_most_played
        )

        doublej = self._abc_radio.doublej_most_played()
        self._update_spotify(doublej, s.playlist_spotify_doublej_most_played)
        self._update_youtube_music(
            doublej, s.playlist_youtube_music_doublej_most_played
        )

        unearthed = self._abc_radio.unearthed_most_played()
        self._update_spotify(unearthed, s.playlist_spotify_unearthed_most_played)
        self._update_youtube_music(
            unearthed, s.playlist_youtube_music_unearthed_most_played
        )

        last_fm = self._last_fm.aus_top_tracks()
        self._update_spotify(last_fm, s.playlist_spotify_last_fm_most_popular_aus)
        self._update_youtube_music(
            last_fm, s.playlist_youtube_music_last_fm_most_popular_aus
        )

        # reduce the 'all-plays' track lists to the top 100 most played

        # classic = self._intermediate.most_played(self._abc_radio.classic_recently_played())

        # jazz = self._intermediate.most_played(self._abc_radio.jazz_recently_played())

        radio_4zzz_plays = self._radio_4zzz.active_program_tracks()
        radio_4zzz = self._intermediate.most_played(radio_4zzz_plays)
        self._update_spotify(radio_4zzz, s.playlist_spotify_radio_4zzz_most_played)
        self._update_youtube_music(
            radio_4zzz, s.playlist_youtube_music_radio_4zzz_most_played
        )

        self._logger.info("Finished updating music playlists")

    def _find_tracks(self, tracks: list[Track], search_func):
        total_count = 0
        found_count = 0
        results = {}
        for track in tracks:
            total_count += 1
            queries = self._intermediate.queries(track)
            query_match = None
            service_found_count = 0
            for query in queries:
                if query in results:
                    query_match = query
                    break
                found_tracks = search_func(query)
                service_found_count += len(found_tracks.tracks)
                match = self._intermediate.match(track, found_tracks.tracks)
                if match:
                    results[query] = match
                    query_match = query
                    break

            if query_match:
                found_count += 1
            else:
                self._logger.warning(
                    f"No match in {len(queries)} queries " f"for track {track}"
                )
                self._logger.warning(
                    f"No match in {service_found_count} service tracks "
                    f"for queries {queries}"
                )

        tracks_percent = float(found_count) / float(total_count + 0.000001)
        current_datetime = datetime.now(tz=self._time_zone)
        found_info = (
            f"Found {found_count} of {total_count} songs ({tracks_percent:.0%})"
        )
        self._logger.warning(found_info)

        # build text for streaming service playlists
        descr = " ".join(
            [
                "This playlist was generated on "
                f"{current_datetime.strftime('%a, %d %b %Y')}.",
                f"{found_info} from the source playlist.",
                "For more information: https://github.com/cofiem/music-playlists",
            ]
        )

        return results, descr

    def _update_spotify(self, track_list: TrackList, playlist_id: str):
        # spotify
        self._logger.info("Find tracks on Spotify.")
        sp_search = self._spotify.search_tracks
        sp_tracks, sp_descr = self._find_tracks(track_list.tracks, sp_search)

        title = track_list.title
        is_public = True
        tracks = [v for k, v in sp_tracks.items()]

        details_result = self._spotify.update_playlist_details(
            playlist_id,
            title,
            sp_descr,
            is_public,
        )
        tracks_result = self._spotify.update_playlist_tracks(
            playlist_id,
            tracks,
        )

        self._logger.info(
            f"Spotify update "
            f"details {'succeeded' if details_result else 'failed'} and "
            f"tracks {'succeeded' if tracks_result else 'failed'}."
        )

    def _update_youtube_music(self, track_list: TrackList, playlist_id: str):
        # youtube music
        self._logger.info("Find tracks on YouTube Music.")
        yt_search = self._youtube_music.search_tracks
        yt_tracks, yt_descr = self._find_tracks(track_list.tracks, yt_search)

        title = track_list.title
        is_public = True
        new_tracks = [v for k, v in yt_tracks.items()]
        old_tracks = self._youtube_music.playlist_tracks(playlist_id).tracks

        details_result = self._youtube_music.update_playlist_details(
            playlist_id,
            title,
            yt_descr,
            is_public,
        )
        tracks_result = self._youtube_music.update_playlist_tracks(
            playlist_id,
            new_tracks,
            old_tracks,
        )

        self._logger.info(
            f"Youtube music update"
            f"details {'succeeded' if details_result else 'failed'} and "
            f"tracks {'succeeded' if tracks_result else 'failed'}."
        )
