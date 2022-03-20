import base64
import secrets
import webbrowser
from logging import Logger
from urllib.parse import urlencode

from requests import Response, codes

from music_playlists.downloader import Downloader


class SpotifyClient:
    def __init__(self, logger: Logger, downloader: Downloader, access_token=None):
        self._logger = logger
        self._downloader = downloader
        self._session = self._downloader.get_session
        self._access_token = access_token

    def get_playlist_tracks(
        self, playlist_id: str, limit: int, offset: int = 0, market: str = "AU"
    ):
        """Get the tracks in a playlist."""
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {
            "fields": "items(track(name,id,artists(name)))",
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def set_playlist_tracks(self, playlist_id: str, song_ids: list[str]):
        """Replace songs in a playlist."""
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {"uris": [f"spotify:track:{song_id}" for song_id in song_ids]}
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        r = self._session.put(url, json=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def set_playlist_details(
        self, playlist_id: str, title: str, description: str, is_public: bool
    ):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        data = {
            "name": title,
            "description": description,
            "public": True if is_public else False,
        }
        headers = {"Authorization": f"Bearer {self._access_token}"}
        r = self._session.put(url, json=data, headers=headers)
        self._check_status(r)
        return r.status_code, None

    def query(self, query: str, limit: int = 5):
        url = f"https://api.spotify.com/v1/search"
        params = {
            "q": query,
            "limit": limit,
            "offset": 0,
            "type": "track",
            "market": "AU",
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def login_authorise(
        self, client_id: str, redirect_uri: str, request_state: str
    ) -> None:
        """Get the url to obtain the Authorization Code."""
        qs = urlencode(
            {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "playlist-modify-public",
                "state": request_state,
            }
        )
        url = "https://accounts.spotify.com/authorize?{qs}".format(qs=qs)
        webbrowser.open(url, new=2)

    def login_token_first(
        self, client_id: str, client_secret: str, auth_code: str, redirect_uri: str
    ) -> tuple[str, str, int]:
        """Get the initial access token and refresh token."""
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        r = self._session.post("https://accounts.spotify.com/api/token", data=data)
        self._check_status(r)
        response = r.json()
        access_token = response.get("access_token")
        expires_in = response.get("expires_in")
        refresh_token = response.get("refresh_token")
        return access_token, refresh_token, expires_in

    def login_token_next(self, client_id: str, client_secret: str, refresh_token: str):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {
            "Authorization": f"Basic {self._login_client_auth(client_id, client_secret)}",
        }
        r = self._session.post(
            "https://accounts.spotify.com/api/token", data=data, headers=headers
        )
        self._check_status(r)
        response = r.json()
        access_token = response.get("access_token")
        self._access_token = access_token
        return True

    def login_init(self, client_id: str, client_secret: str):
        # ref: https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
        request_state = secrets.token_hex(10)
        redirect_uri = "https://www.anotherbyte.net/callback"

        self.login_authorise(client_id, redirect_uri, request_state)
        auth_code = input("Enter the 'code' from the authorisation url:")

        access_token, refresh_token, expires_in = self.login_token_first(
            client_id, client_secret, auth_code, redirect_uri
        )
        return access_token, refresh_token, expires_in

    def _login_client_auth(self, client_id: str, client_secret: str):
        basic = f"{client_id}:{client_secret}"
        basic_b64 = base64.b64encode(basic.encode())
        return basic_b64.decode()

    def _check_status(self, r: Response):
        expected_codes = [codes.ok, codes.created]
        if r.status_code not in expected_codes:
            raise ValueError(f"Error in response - {r.status_code}:{r.text}.")
