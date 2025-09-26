import base64
import logging
import secrets
import webbrowser

from dataclasses import field
from urllib.parse import urlencode

import attrs

from beartype import beartype
from requests import Response, codes

from music_playlists import intermediate as inter
from music_playlists import model, utils


logger = logging.getLogger(__name__)


@beartype
@attrs.frozen
class ExternalUrl:
    spotify: str


@beartype
@attrs.frozen
class Image:
    url: str
    height: int
    width: int


@beartype
@attrs.frozen
class Follower:
    href: str
    total: int


@beartype
@attrs.frozen
class Artist:
    external_urls: ExternalUrl
    href: str
    id: str
    name: str
    type: str
    uri: str
    popularity: int | None = None
    images: list[Image] | None = None
    genres: list[str] | None = None
    followers: list[Follower] | None = None


@beartype
@attrs.frozen
class Album:
    album_type: str
    total_tracks: int
    external_urls: ExternalUrl
    href: str
    id: str
    images: list[Image]
    name: str
    release_date: str
    release_date_precision: str
    type: str
    uri: str
    album_group: str | None = None
    artists: list[Artist] | None = None
    available_markets: list[str] | None = None
    is_playable: bool | None = None


@beartype
@attrs.frozen
class ExternalId:
    isrc: str | None = None
    """International Standard Recording Code"""

    ean: str | None = None
    """"International Article Number"""

    upc: str | None = None
    """Universal Product Code"""


@beartype
@attrs.frozen
class Restriction:
    reason: str


@beartype
@attrs.frozen
class Track:
    external_urls: ExternalUrl
    href: str
    id: str
    type: str
    uri: str
    name: str | None = None
    album: Album | None = None
    external_ids: ExternalId | None = None
    popularity: int | None = None
    track_number: int | None = None
    is_local: bool | None = None
    is_playable: bool | None = None
    explicit: bool | None = None
    duration_ms: int | None = None
    disc_number: int | None = None
    artists: list[Artist] = field(default_factory=list)
    preview_url: str | None = None
    episode: bool | None = None
    track: bool | None = None
    restrictions: Restriction | None = None
    linked_from: str = None
    available_markets: list[str] | None = None


@beartype
@attrs.frozen
class Tracks:
    items: list[Track]
    href: str | None = None
    limit: int | None = None
    next: str | None = None
    offset: int | None = None
    previous: str | None = None
    total: int | None = None


@beartype
class Client(model.ServiceClient):
    auth_header = "Authorization"

    def __init__(
        self,
        downloader: utils.Downloader,
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

        self._session = self._downloader.get_session

        self._url_api = "https://api.spotify.com/v1"
        self._url_accounts = "https://accounts.spotify.com"

        if not redirect_uri or not client_id or not client_secret:
            raise Exception(
                "Must provide redirect_uri and client_id and client_secret.",
            )

        # ref: https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow

    @property
    def access_token(self):
        if not self._access_token:
            raise ValueError("Log in to Spotify first.")
        return self._access_token

    @property
    def auth_value(self):
        result = f"Bearer {self.access_token}"
        return result

    def login(self) -> None:
        if self._refresh_token and not self._access_token:
            self._get_access_token()
        if not self._refresh_token:
            self._get_refresh_token()

    def _get_access_token(self) -> None:
        logger.info("Login using Spotify refresh token.")

        data = {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
        basic_auth = self._login_client_auth(self._client_id, self._client_secret)
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        url = f"{self._url_accounts}/api/token"

        r = self._session.post(url, data=data, headers=headers)
        self._check_status(r)

        data = r.json()
        self._access_token = data.get("access_token")

    def _get_refresh_token(self) -> None:
        logger.info("Login using Spotify authorisation flow.")

        auth_qs = urlencode(
            {
                "client_id": self._client_id,
                "response_type": "code",
                "redirect_uri": self._redirect_uri,
                "scope": "playlist-modify-public",
                "state": secrets.token_hex(10),
            },
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
        r = self._session.post(token_url, data=token_qs)
        self._check_status(r)

        response = r.json()
        self._access_token = response.get("access_token")
        self._refresh_token = response.get("refresh_token")

        logger.info("Refresh token: %s", self._refresh_token)

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
                f"status '{r.status_code}' content '{r.text}'.",
            )


@beartype
class Manage(model.Service):
    code = "spotify"

    def __init__(self, downloader: utils.Downloader, client: Client):
        self._downloader = downloader
        self._client = client
        self._session = self._downloader.get_session

        self._url_api = "https://api.spotify.com/v1"
        self._url_accounts = "https://accounts.spotify.com"

    @property
    def client(self):
        return self._client

    def playlist_tracks(
        self,
        playlist_id: str,
        limit: int = 100,
        offset: int = 0,
        market: str = "AU",
        *args,
        **kwargs,
    ) -> Tracks:
        """Get the tracks in a playlist."""
        logger.info("Get playlist tracks from Spotify for %s.", playlist_id)

        if not playlist_id:
            raise ValueError
        limit = max(limit, 1)
        offset = max(offset, 0)
        if not market:
            market = "AU"

        url = f"{self._url_api}/playlists/{playlist_id}/tracks"
        params = {
            "fields": "items(track(*))",
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        return utils.c.structure(
            {"items": [t["track"] for t in r.json()["items"]]},
            Tracks,
        )

    def track_embedded_id(self, track: inter.Track) -> inter.Track | None:
        # search = json.dumps(attrs.asdict(track))
        # if "spotify" in search:
        #     raise ValueError(search)
        return None

    def search_tracks(
        self,
        query: str,
        limit: int = 5,
        offset: int = 0,
        market: str = "AU",
    ) -> inter.TrackList:
        logger.debug("Search tracks from Spotify for '%s'.", query)

        limit = max(limit, 1)
        offset = max(offset, 0)
        if not market:
            market = "AU"

        url = f"{self._url_api}/search"
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "type": "track",
            "market": market,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.get(url, params=params, headers=headers)
        self._check_status(r)
        ts = utils.c.structure(r.json()["tracks"], Tracks)
        results = [self._convert_track(t) for t in ts.items]
        return inter.TrackList(
            title=None, type=inter.TrackListType.ORDERED, tracks=results
        )

    def update_playlist_tracks(self, info: inter.ServicePlaylistTracks) -> bool:
        """Replace songs in a playlist."""
        logger.info("Update Spotify playlist tracks for %s.", info.playlist_id)

        url = f"{self._url_api}/playlists/{info.playlist_id}/tracks"
        params = {"uris": [t.raw.uri for t in info.tracks]}
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.put(url, json=params, headers=headers)
        self._check_status(r)
        # snapshot_id = r.get('snapshot_id')
        return r.status_code in [codes.created, codes.ok]

    def update_playlist_details(self, info: inter.ServicePlaylistInfo) -> bool:
        logger.info("Update Spotify playlist details for %s.", info.playlist_id)

        url = f"{self._url_api}/playlists/{info.playlist_id}"
        data = {
            "name": info.title,
            "description": info.description,
            "public": True if info.is_public else False,
        }
        headers = {self._client.auth_header: self._client.auth_value}
        r = self._session.put(url, json=data, headers=headers)
        self._check_status(r)
        return r.status_code == codes.ok

    def _check_status(self, r: Response):
        expected_codes = [codes.ok, codes.created]
        if r.status_code not in expected_codes:
            raise ValueError(
                f"Error in response url '{r.url}' "
                f"status '{r.status_code}' content '{r.text}'.",
            )

    def _convert_track(self, item: Track):
        return inter.Track(
            origin_code=self.code,
            track_id=item.id,
            title=item.name,
            artists=[a.name for a in item.artists],
            raw=item,
        )
