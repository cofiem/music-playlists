import functools
import logging
import typing

from pathlib import Path

import attrs
import ytmusicapi.helpers

from beartype import beartype
from requests.structures import CaseInsensitiveDict
from ytmusicapi import OAuthCredentials, YTMusic
from ytmusicapi.exceptions import YTMusicServerError

from music_playlists import intermediate as inter
from music_playlists import model, utils


logger = logging.getLogger(__name__)


@beartype
@attrs.frozen
class Album:
    name: str
    id: str


@beartype
@attrs.frozen
class Artist:
    name: str
    id: str | None = None
    type: str | None = None


@beartype
@attrs.frozen
class Author:
    name: str
    id: str


@beartype
@attrs.frozen
class Feedback:
    add: str | None
    remove: str | None


@beartype
@attrs.frozen
class Thumbnail:
    url: str
    width: int
    height: int


@beartype
@attrs.frozen
class Track:
    title: str
    artists: list[Artist]
    thumbnails: list[Thumbnail]
    isExplicit: bool
    duration: str | None = None
    duration_seconds: int | None = None
    videoId: str | None = None
    views: str | None = None
    album: Album | None = None
    feedbackTokens: Feedback | None = None
    isAvailable: bool | None = None
    likeStatus: str | None = None
    setVideoId: str | None = None
    year: str | None = None
    category: str | None = None
    resultType: str | None = None
    videoType: str | None = None
    inLibrary: bool | None = None
    listenAgainFeedbackTokens: str | None = None
    pinnedToListenAgain: str | None = None


@beartype
@attrs.frozen
class Playlist:
    id: str
    privacy: str
    title: str
    thumbnails: list[Thumbnail]
    description: str
    trackCount: int
    # suggestions_token: str
    tracks: list[Track]
    duration: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    related: str | None = None
    owned: str | None = None
    artists: str | None = None
    views: str | None = None
    author: Author | None = None


@beartype
@attrs.frozen
class Tracks:
    pass


@beartype
class Client(model.ServiceClient):
    def __init__(
        self, downloader: utils.Downloader, credentials: dict[str, str] | None = None
    ):
        self._downloader = downloader
        self._credentials = self._build_expected_credentials(credentials)
        self._session = self._downloader.get_session
        self._api: YTMusic | None = None

    @property
    def api(self):
        if not self._api:
            raise ValueError("Log in to YouTube music first.")
        return self._api

    def login(self) -> None:
        if not self._credentials:
            self._get_credentials()

        logger.info("Login using YouTube Music credentials.")
        s = self._session
        s.request = functools.partial(s.request, timeout=30)
        cred_type, creds = self._credentials.get("type"), self._credentials.get("data")
        if cred_type == "oauth":
            self._api = YTMusic(
                auth=creds.get("auth"),
                requests_session=s,
                oauth_credentials=OAuthCredentials(
                    client_id=creds.get("client_id"),
                    client_secret=creds.get("client_secret"),
                ),
            )
        elif cred_type == "browser":
            self._api = YTMusic(auth=creds, requests_session=s)
        else:
            raise ValueError(f"Unknown credential type '{cred_type}'.")

    def _get_credentials(self):
        logger.info("Get YouTube Music credentials.")

        file_path = input(
            "Enter the file path to the request headers from https://music.youtube.com:",
        )
        if not file_path:
            raise ValueError("Provide the file path.")
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"Invalid file path '{path}'.")

        request_headers = path.read_text()
        self._credentials = YTMusic.setup(filepath=None, headers_raw=request_headers)

    def _build_expected_credentials(
        self, raw: dict[str, str] | None
    ) -> CaseInsensitiveDict[str] | dict[str, typing.Any]:
        """Check headers required for auth and build the credentials data"""

        if "Cookie" in raw and "X-Goog-AuthUser" in raw and "Authorization" in raw:
            data = {k.lower(): v for k, v in (raw or {}).items()}
            result = ytmusicapi.helpers.initialize_headers()
            required = ["cookie", "x-goog-authuser", "authorization"]
            for item in required:
                if item not in data:
                    msg = f"Missing required item in credentials '{item}'."
                    raise ValueError(msg)
                result[item] = data.get(item)
            return {"type": "browser", "data": result}
        if "auth" in raw and "client_id" in raw and "client_secret" in raw:
            return {"type": "oauth", "data": raw}
        return {}


@beartype
class Manage(model.Service):
    code = "youtube-music"

    def __init__(self, downloader: utils.Downloader, client: Client):
        self._downloader = downloader
        self._client = client
        self._session = self._downloader.get_session

    @property
    def client(self):
        return self._client

    def playlist_tracks(
        self, playlist_id: str, limit: int | None = 100, *args, **kwargs
    ) -> inter.TrackList:
        logger.info("Get playlist tracks from YouTube Music for %s.", playlist_id)

        if limit is None:
            raw = self._client.api.get_playlist(playlist_id)
        else:
            raw = self._client.api.get_playlist(playlist_id, limit)

        pl = utils.c.structure(raw, Playlist)
        results = [self._convert_track(t) for t in pl.tracks]
        return inter.TrackList(
            title=None, type=inter.TrackListType.ORDERED, tracks=results
        )

    def track_embedded_id(self, track: inter.Track) -> inter.Track | None:
        # search = json.dumps(attrs.asdict(track))
        # if "youtube" in search:
        #     raise ValueError(search)
        return None

    def search_tracks(
        self, query: str, limit: int | None = 5, *args, **kwargs
    ) -> inter.TrackList:
        logger.debug("Search tracks from YouTube Music for '%s'.", query)

        raw = self._client.api.search(
            query=query,
            filter="songs",
            limit=limit,
            ignore_spelling=False,
        )
        ts = utils.c.structure(raw, list[Track])
        results = [self._convert_track(t) for t in ts]
        return inter.TrackList(
            title=None, type=inter.TrackListType.ORDERED, tracks=results
        )

    def update_playlist_tracks(self, info: inter.ServicePlaylistTracks) -> bool:
        logger.info("Update YouTube Music playlist tracks for %s.", info.playlist_id)

        old_tracks = self.playlist_tracks(info.playlist_id, None).tracks
        new_tracks = info.tracks

        if old_tracks:
            try:
                result = self._client.api.remove_playlist_items(
                    info.playlist_id,
                    [
                        {
                            "videoId": t.raw.videoId,
                            "setVideoId": t.raw.setVideoId,
                        }
                        for t in old_tracks
                    ],
                )

                if result != "STATUS_SUCCEEDED":
                    return False
            except ytmusicapi.exceptions.YTMusicServerError as e:
                logger.error("Could not remove playlist item: ", str(e))
                return False

        try:
            result = self._client.api.add_playlist_items(
                info.playlist_id,
                [t.raw.videoId for t in new_tracks],
                source_playlist=None,
                duplicates=False,
            )
            if "status" not in result or result.get("status") != "STATUS_SUCCEEDED":
                return False
            return True
        except YTMusicServerError as e:
            logger.error("Could not add playlist item: ", str(e))
            return False

    def update_playlist_details(self, info: inter.ServicePlaylistInfo) -> bool:
        logger.info("Update YouTube Music playlist details for %s.", info.playlist_id)

        try:
            result = self._client.api.edit_playlist(
                playlistId=info.playlist_id,
                title=info.title,
                description=info.description,
                privacyStatus="PUBLIC" if info.is_public else "PRIVATE",
            )
            return result == "STATUS_SUCCEEDED"
        except ytmusicapi.exceptions.YTMusicServerError as e:
            logger.error("Could not update playlist: ", str(e))
            return False

    def _convert_track(self, item: Track):
        return inter.Track(
            origin_code=self.code,
            track_id=item.videoId,
            title=item.title,
            artists=[a.name for a in item.artists],
            raw=item,
        )
