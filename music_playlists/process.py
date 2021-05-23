import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, Optional

import pytz

from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.music_service.spotify import Spotify
from music_playlists.music_service.youtube_music import YouTubeMusic
from music_playlists.music_source.doublej_most_played import DoubleJMostPlayed
from music_playlists.music_source.last_fm_most_popular import LastFmMostPopular
from music_playlists.music_source.radio4zzz_most_played import Radio4zzzMostPlayed
from music_playlists.music_source.source_playlist import SourcePlaylist
from music_playlists.music_source.triplej_most_played import TripleJMostPlayed
from music_playlists.music_source.triplej_unearthed_chart import TripleJUnearthedChart
from music_playlists.track import Track


class Process:
    _logger = logging.getLogger("music-playlists")

    def __init__(self):
        self._base_path = None
        self._downloader = None  # type: Optional[Downloader]
        self._time_zone = None  # type: datetime.tzinfo
        self._lastfm_api_key = None  # type: Optional[str]
        self._lastfm = None  # type: Optional[LastFmMostPopular]
        self._radio_4zzz = None  # type: Optional[Radio4zzzMostPlayed]
        self._sc_client_id = None  # type: Optional[str]
        # self._soundcloud = None  # type: Optional[SoundCloudTrending]
        self._double_j = None  # type: Optional[DoubleJMostPlayed]
        self._triple_j = None  # type: Optional[TripleJMostPlayed]
        self._triple_j_unearthed = None  # type: Optional[TripleJUnearthedChart]

        self._spotify = None  # type: Optional[Spotify]
        self._youtube_music = None  # type: Optional[YouTubeMusic]

    @property
    def default_settings(self):
        return {
            "time_zone": "MUSIC_PLAYLISTS_TIME_ZONE",
            "base_path": "MUSIC_PLAYLISTS_BASE_PATH",
            "lastfm_api_key": "LASTFM_AUTH_API_KEY",
            # "soundcloud_client_id": "SOUNDCLOUD_CLIENT_ID",
            "spotify_refresh_token": "SPOTIFY_AUTH_REFRESH_TOKEN",
            "spotify_client_id": "SPOTIFY_AUTH_CLIENT_ID",
            "spotify_client_secret": "SPOTIFY_AUTH_CLIENT_SECRET",
            "youtube_music_config": "YOUTUBE_MUSIC_AUTH_CONFIG",
            "playlists": {
                Spotify.code: {
                    LastFmMostPopular.code: "SPOTIFY_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS",
                    # SoundCloudTrending.code: "SPOTIFY_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS",
                    Radio4zzzMostPlayed.code: "SPOTIFY_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED",
                    DoubleJMostPlayed.code: "SPOTIFY_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED",
                    TripleJMostPlayed.code: "SPOTIFY_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED",
                    TripleJUnearthedChart.code: "SPOTIFY_PLAYLIST_ID_TRIPLEJ_UNEARTHED",
                },
                YouTubeMusic.code: {
                    LastFmMostPopular.code: "YOUTUBE_MUSIC_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS",
                    # SoundCloudTrending.code: "YOUTUBE_MUSIC_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS",
                    Radio4zzzMostPlayed.code: "YOUTUBE_MUSIC_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED",
                    DoubleJMostPlayed.code: "YOUTUBE_MUSIC_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED",
                    TripleJMostPlayed.code: "YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED",
                    TripleJUnearthedChart.code: "YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_UNEARTHED",
                },
            },
        }

    def initialise(self, settings: dict[str, Union[str, dict[str, str]]]):
        self._logger.info("Setting up access to music services.")

        logger = self._logger
        base_path = Path(self._get_setting(settings, "base_path"))
        downloader = Downloader(logger, base_path)

        time_zone = pytz.timezone(self._get_setting(settings, "time_zone"))

        self._get_spotify(logger, downloader, time_zone, settings, initialise=True)
        self._get_youtube_music(
            logger, downloader, time_zone, settings, initialise=True
        )

        self._logger.info("Finished setting up access to music services.")
        return True

    def run(self, settings: dict[str, Union[str, dict[str, str]]]):
        self._logger.info("Updating music playlists.")

        datetime_now = datetime.now(tz=self._time_zone).isoformat()

        self.build(settings)

        # obtain the track information and normalise the track details
        limit = 100
        source_playlists = {
            Radio4zzzMostPlayed.code: self._radio_4zzz,
            LastFmMostPopular.code: self._lastfm,
            TripleJMostPlayed.code: self._triple_j,
            TripleJUnearthedChart.code: self._triple_j_unearthed,
            DoubleJMostPlayed.code: self._double_j,
        }  # type: dict[str, SourcePlaylist]

        # find songs in streaming services and build new playlists
        services = {
            Spotify.code: self._spotify,
            YouTubeMusic.code: self._youtube_music,
        }  # type: dict[str, ServicePlaylist]

        playlist_ids = settings.get("playlists", {})  # type: dict[str, dict[str, str]]
        for service_code, playlists in playlist_ids.items():
            service = services[service_code]
            for playlist_code, playlist_key in playlists.items():

                cache_name = self._downloader.cache_persisted
                cache_key = "-".join([service_code, playlist_code])
                last_updated = self._downloader.retrieve_object(cache_name, cache_key)
                if last_updated:
                    cache_value = last_updated.get_value()
                    hours_ago = 6
                    twelve_hours_ago = (
                        datetime.now(tz=self._time_zone) - timedelta(hours=hours_ago)
                    ).isoformat()
                    if cache_value and cache_value > twelve_hours_ago:
                        self._logger.warning(
                            f"Skipping playlist '{playlist_code}' for '{service_code}' "
                            f"because it was updated less than {hours_ago} hours ago."
                        )
                        continue

                playlist_id = self._get_setting(playlists, playlist_code)
                tracks_current = service.get_playlist_tracks(playlist_id)
                tracks_source = source_playlists.get(playlist_code)
                tracks_new = tracks_source.get_playlist_tracks(limit)
                if not tracks_new:
                    self._logger.warning(
                        f"Skipping playlist '{playlist_code}' for '{service_code}' as there are no new tracks."
                    )
                    continue

                tracks_add, description = service.build_new_playlist(
                    tracks_current, tracks_new, self._time_zone
                )
                service.set_playlist_details(
                    playlist_id, tracks_source.title, description, is_public=True
                )
                result = service.set_playlist_tracks(
                    playlist_id, tracks_add, tracks_current
                )
                if not result:
                    self._logger.error(
                        f"Error updating playlist '{playlist_code}' for '{service_code}'."
                    )

                self._downloader.store_object(cache_name, cache_key, datetime_now)

        self._logger.info("Finished updating music playlists")

    def build(self, settings: dict[str, Union[str, dict[str, str]]]):
        self._logger.info("Starting up.")

        logger = self._logger
        base_path = Path(self._get_setting(settings, "base_path"))
        downloader = Downloader(logger, base_path)

        time_zone = pytz.timezone(self._get_setting(settings, "time_zone"))

        lastfm_api_key = self._get_setting(settings, "lastfm_api_key")
        lastfm = LastFmMostPopular(logger, downloader, lastfm_api_key)

        radio_4zzz = Radio4zzzMostPlayed(logger, downloader, time_zone)

        # sc_client_id = self._get_setting(settings, "soundcloud_client_id")
        # soundcloud = SoundCloudTrending(logger, downloader, sc_client_id)

        double_j = DoubleJMostPlayed(logger, downloader, time_zone)
        triple_j = TripleJMostPlayed(logger, downloader, time_zone)
        triple_j_unearthed = TripleJUnearthedChart(self._logger, downloader)

        spotify = self._get_spotify(
            logger, downloader, time_zone, settings, initialise=False
        )
        youtube_music = self._get_youtube_music(
            logger, downloader, time_zone, settings, initialise=False
        )

        self._base_path = base_path
        self._downloader = downloader
        self._time_zone = time_zone
        self._lastfm_api_key = lastfm_api_key
        self._lastfm = lastfm
        self._radio_4zzz = radio_4zzz
        # self._sc_client_id = sc_client_id
        # self._soundcloud = soundcloud
        self._double_j = double_j
        self._triple_j = triple_j
        self._triple_j_unearthed = triple_j_unearthed

        self._spotify = spotify
        self._youtube_music = youtube_music

        self._logger.info("Finished starting up.")

    def _get_setting(self, settings: dict[str, Union[str, dict[str, str]]], name: str):
        key = settings.get(name)
        if key is None:
            raise ValueError(f"Could not retrieve key for env var '{name}'.")

        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Could not retrieve value for env var '{name}:{key}'.")

        return value

    def _get_spotify(
        self,
        logger: logging.Logger,
        downloader: Downloader,
        time_zone: datetime.tzinfo,
        settings: dict[str, Union[str, dict[str, str]]],
        initialise: bool,
    ):
        spotify_client_id = self._get_setting(settings, "spotify_client_id")
        spotify_client_secret = self._get_setting(settings, "spotify_client_secret")
        spotify_refresh_token = self._get_setting(settings, "spotify_refresh_token")
        spotify = Spotify(logger, downloader, time_zone)

        if initialise and not spotify_refresh_token:
            result = spotify.login_init(spotify_client_id, spotify_client_secret)
            if result is not True:
                raise ValueError("Could not initialise Spotify, check the settings.")

        elif initialise and spotify_refresh_token:
            logger.warning("Spotify refresh token is already available, nothing to do.")
        elif not initialise and not spotify_refresh_token:
            raise ValueError("Spotify must be initialised first.")
        elif not initialise and spotify_refresh_token:
            spotify.login(
                spotify_refresh_token, spotify_client_id, spotify_client_secret
            )
        else:
            raise ValueError("Spotify is in an unknown state.")
        return spotify

    def _get_youtube_music(
        self,
        logger: logging.Logger,
        downloader: Downloader,
        time_zone: datetime.tzinfo,
        settings: dict[str, Union[str, dict[str, str]]],
        initialise: bool,
    ):
        youtube_music_config = self._get_setting(settings, "youtube_music_config")
        youtube_music = YouTubeMusic(logger, downloader, time_zone)

        if initialise and not youtube_music_config:
            result = youtube_music.login(youtube_music_config)
            if result is not True:
                raise ValueError(
                    "Could not initialise YouTube Music, check the settings."
                )
        elif initialise and youtube_music_config:
            logger.warning(
                "YouTube Music auth config is already available, nothing to do."
            )
        elif not initialise and not youtube_music_config:
            raise ValueError("YouTube Music must be initialised first.")
        elif not initialise and youtube_music_config:
            youtube_music.login(youtube_music_config)
        else:
            raise ValueError("YouTube Music is in an unknown state.")
        return youtube_music
