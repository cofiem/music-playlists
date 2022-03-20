import functools
import logging
from pathlib import Path
from typing import List, Optional

from ytmusicapi import YTMusic

from music_playlists.downloader import Downloader
from music_playlists.music_service.service_playlist import ServicePlaylist
from music_playlists.track import Track


class YouTubeMusic(ServicePlaylist):
    """Manages playlists for YouTube Music."""

    code = "ytmusic"

    def __init__(self, logger: logging.Logger, downloader: Downloader, time_zone):
        super().__init__(logger, downloader, time_zone)
        self._client = None  # type: Optional[YTMusic]

    def login_init(self):
        self._logger.info("Initialise YouTube Music login.")
        file_path = input(
            "Paste the file path to the request headers from https://music.youtube.com:"
        )
        if not file_path:
            raise ValueError("Provide the file path.")
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"Invalid file path '{path}'.")

        request_headers = path.read_text()
        creds_json = YTMusic.setup(filepath=None, headers_raw=request_headers)
        self._logger.warning(f"YouTubeMusic credentials: {creds_json}")
        return True

    def login(self, credentials: str):
        self._logger.info("Login to YouTube Music.")
        s = self._downloader.get_session
        s.request = functools.partial(s.request, timeout=30)
        self._client = YTMusic(auth=credentials, requests_session=s)
        return True

    def get_playlist_tracks(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> List[Track]:
        self._logger.info(f"Retrieving tracks for YouTube Music playlist.")
        if limit is None:
            raw = self._client.get_playlist(playlist_id)
        else:
            raw = self._client.get_playlist(playlist_id, limit)
        result = []
        for track in raw.get("tracks", []):
            result.append(
                Track(
                    origin_code=self.code,
                    track_id=track.get("videoId"),
                    title=track.get("title"),
                    artists=[a.get("name") for a in track.get("artists")],
                    info=track,
                    query_strings=[],
                )
            )
        return result

    def set_playlist_tracks(
        self, playlist_id: str, new_tracks: List[Track], old_tracks: List[Track]
    ) -> bool:
        self._logger.info(
            f"Setting {len(new_tracks)} tracks for YouTube Music playlist."
        )
        if old_tracks:
            result = self._client.remove_playlist_items(
                playlist_id,
                [
                    {
                        "videoId": t.track_id,
                        "setVideoId": t.info.get("setVideoId"),
                    }
                    for t in old_tracks
                ],
            )

            if result != "STATUS_SUCCEEDED":
                return False

        result = self._client.add_playlist_items(
            playlist_id,
            [t.track_id for t in new_tracks],
            source_playlist=None,
            duplicates=False,
        )
        if "status" not in result or result.get("status") != "STATUS_SUCCEEDED":
            return False
        return True

    def set_playlist_details(
        self,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        self._logger.info(f"Setting details for YouTube Music playlist '{title}'.")
        result = self._client.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus="PUBLIC" if is_public else "PRIVATE",
        )
        return result == "STATUS_SUCCEEDED"

    def find_track(self, query: str, limit: int = 5) -> list[Track]:
        self._logger.debug(f"Looking for YouTube Music track matching '{query}'.")

        # cache response and use cache if available
        query_result = self._client.search(
            query=query, filter="songs", limit=limit, ignore_spelling=False
        )

        result = []
        for track in query_result:
            result.append(
                Track(
                    origin_code=self.code,
                    track_id=track.get("videoId"),
                    title=track.get("title"),
                    artists=[a.get("name") for a in track.get("artists")],
                    info=track,
                    query_strings=[],
                )
            )
        return result
