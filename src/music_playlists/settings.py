import os
import pathlib
import tomllib

from beartype import beartype


@beartype
class Settings:
    def __init__(self):
        self._p = pathlib.Path.cwd().joinpath(".env.toml")
        self._data = {}
        if self._p.exists():
            self._data = tomllib.loads(self._p.read_text(encoding="utf-8"))

    @property
    def time_zone(self):
        return self._get_setting("MUSIC_PLAYLISTS_TIME_ZONE")

    @property
    def base_path(self):
        return self._get_setting("MUSIC_PLAYLISTS_BASE_PATH")

    @property
    def lastfm_api_key(self):
        return self._get_setting("LASTFM_AUTH_API_KEY")

    @property
    def spotify_refresh_token(self):
        return self._get_setting("SPOTIFY_AUTH_REFRESH_TOKEN")

    @property
    def spotify_client_id(self):
        return self._get_setting("SPOTIFY_AUTH_CLIENT_ID")

    @property
    def spotify_client_secret(self):
        return self._get_setting("SPOTIFY_AUTH_CLIENT_SECRET")

    @property
    def spotify_redirect_uri(self):
        return self._get_setting("SPOTIFY_AUTH_REDIRECT_URI")

    @property
    def youtube_music_config(self):
        return self._get_setting("YOUTUBE_MUSIC_AUTH_CONFIG")

    @property
    def playlist_spotify_last_fm_most_popular_aus(self):
        return self._get_setting("SPOTIFY_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS")

    @property
    def playlist_spotify_radio_4zzz_most_played(self):
        return self._get_setting("SPOTIFY_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED")

    @property
    def playlist_spotify_doublej_most_played(self):
        return self._get_setting("SPOTIFY_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED")

    @property
    def playlist_spotify_triplej_most_played(self):
        return self._get_setting("SPOTIFY_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED")

    @property
    def playlist_spotify_unearthed_most_played(self):
        return self._get_setting("SPOTIFY_PLAYLIST_ID_TRIPLEJ_UNEARTHED")

    @property
    def playlist_youtube_music_last_fm_most_popular_aus(self):
        return self._get_setting("YOUTUBE_MUSIC_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS")

    @property
    def playlist_youtube_music_radio_4zzz_most_played(self):
        return self._get_setting("YOUTUBE_MUSIC_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED")

    @property
    def playlist_youtube_music_doublej_most_played(self):
        return self._get_setting("YOUTUBE_MUSIC_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED")

    @property
    def playlist_youtube_music_triplej_most_played(self):
        return self._get_setting("YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED")

    @property
    def playlist_youtube_music_unearthed_most_played(self):
        return self._get_setting("YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_UNEARTHED")

    def _get_setting(self, key: str):
        value = None
        if self._data:
            value = self._data.get(key)

        if value is None:
            value = os.getenv(key)

        if value is None:
            raise ValueError(f"Could not retrieve value for env var '{key}'.")

        return value
