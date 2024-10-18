import base64
import logging
import secrets
import webbrowser
from urllib.parse import urlencode

from requests import Response, codes

from music_playlists.downloader import Downloader

logger = logging.getLogger("spotify-client")


class Client:
    auth_header = "Authorization"

    def __init__(
        self,
        downloader: Downloader,
        redirect_uri: str,
        client_id: str,
        client_secret: str,
        refresh_token: str | None = None,
        access_token: str | None = None,
    ):
        self._downloader = downloader
        self._redirect_uri = redirect_uri
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token = access_token

        self._session_no_cache = self._downloader.get_session_no_cache

        self._url_api = "https://api.spotify.com/v1"
        self._url_accounts = "https://accounts.spotify.com"

        if not redirect_uri or not client_id or not client_secret:
            raise Exception(
                "Must provide redirect_uri and client_id and client_secret."
            )

        # ref: https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow

    @property
    def access_token(self):
        if not self._access_token:
            raise ValueError("Log in to spotify first.")
        return self._access_token

    @property
    def auth_value(self):
        return f"Bearer {self.access_token}"

    def login(self):
        if self._refresh_token and not self._access_token:
            self._get_access_token()
        if not self._refresh_token:
            self._get_refresh_token()

    def _get_access_token(self) -> None:
        logger.info("Login using Spotify refresh token.")

        data = {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
        basic_auth = self._login_client_auth(self._client_id, self._client_secret)
        headers = {"Authorization": f"Basic {basic_auth}"}
        url = f"{self._url_accounts}/api/token"

        r = self._session_no_cache.post(url, data=data, headers=headers)
        self._check_status(r)

        self._access_token = r.json().get("access_token")

    def _get_refresh_token(self) -> None:
        logger.info("Login using Spotify authorisation flow.")

        auth_qs = urlencode(
            {
                "client_id": self._client_id,
                "response_type": "code",
                "redirect_uri": self._redirect_uri,
                "scope": "playlist-modify-public",
                "state": secrets.token_hex(10),
            }
        )
        auth_url = f"{self._url_accounts}/authorize?{auth_qs}"
        webbrowser.open(auth_url, new=2)

        auth_code = input("Enter the 'code' from the authorisation url:")

        token_url = f"{self._url_accounts}/api/token"
        token_qs = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self._redirect_uri,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        r = self._session_no_cache.post(token_url, data=token_qs)
        self._check_status(r)

        response = r.json()
        self._access_token = response.get("access_token")
        self._refresh_token = response.get("refresh_token")

        expires_in = response.get("expires_in")
        logger.info(f"Spotify access token expires in {expires_in / 60.0 / 60.0} hours")

    def _login_client_auth(self, client_id: str, client_secret: str):
        basic = f"{client_id}:{client_secret}"
        basic_b64 = base64.b64encode(basic.encode())
        return basic_b64.decode()

    def _check_status(self, r: Response):
        expected_codes = [codes.ok, codes.created]
        if r.status_code not in expected_codes:
            raise ValueError(
                f"Error in response url '{r.url}' "
                f"status '{r.status_code}' content '{r.text}'."
            )
