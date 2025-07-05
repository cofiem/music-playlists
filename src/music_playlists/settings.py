import pathlib
import tomllib
from dataclasses import dataclass

from beartype import beartype


@beartype
@dataclass(frozen=True)
class PlaylistSetting:
    source: str
    service: str
    code: str
    title: str
    playlist_id: str


@beartype
class Settings:
    def __init__(self, config_path: pathlib.Path):
        self._p = config_path
        self._data = {}
        if self._p.exists():
            self._data = tomllib.loads(self._p.read_text(encoding="utf-8"))

    @property
    def time_zone(self):
        return self._get_setting("general", "time_zone")

    @property
    def base_path(self):
        return self._get_setting("general", "base_path")

    @property
    def lastfm_api_key(self):
        return self._get_setting("secrets", "last-fm", "api_key")

    @property
    def spotify_refresh_token(self):
        return self._get_setting("secrets", "spotify", "auth_refresh_token")

    @property
    def spotify_client_id(self):
        return self._get_setting("secrets", "spotify", "auth_client_id")

    @property
    def spotify_client_secret(self):
        return self._get_setting("secrets", "spotify", "auth_client_secret")

    @property
    def spotify_redirect_uri(self):
        return self._get_setting("secrets", "spotify", "auth_redirect_uri")

    @property
    def youtube_music_config(self):
        return {
            "X-Goog-AuthUser": self._get_setting(
                "secrets", "youtube-music", "x_goog_auth_user"
            ),
            "Cookie": self._get_setting("secrets", "youtube-music", "cookie"),
            "Authorization": self._get_setting(
                "secrets", "youtube-music", "authorization"
            ),
        }

    @property
    def playlists(self):
        items = self._get_setting("playlists")
        for item in items:
            yield PlaylistSetting(**item)

    def _get_setting(self, *args):
        d = self._data or {}
        value = None
        if d:
            current = {**d}
            for arg in args:
                current = (current or {}).get(arg)
            if current != d:
                value = current

        # if value is None:
        #     value = os.getenv(key)

        if value is None:
            raise ValueError(f"Could not retrieve value for '{'.'.join(args)}'.")

        return value
