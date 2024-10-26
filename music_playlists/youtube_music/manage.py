import logging

from beartype import beartype
from ytmusicapi.exceptions import YTMusicServerError

from music_playlists.downloader import Downloader
from music_playlists.intermediate.models import TrackList, Track as Track
from music_playlists.intermediate.serialization import c
from music_playlists.youtube_music import models
from music_playlists.youtube_music.client import Client


logger = logging.getLogger("youtube-music-manage")


@beartype
class Manage:
    code = "youtube-music"

    def __init__(self, downloader: Downloader, client: Client):
        self._downloader = downloader
        self._client = client
        self._session = self._downloader.get_session

    @property
    def client(self):
        return self._client

    def playlist_tracks(self, playlist_id: str, limit: int | None = 100) -> TrackList:
        logger.info("Get playlist tracks from youtube music.")

        if limit is None:
            raw = self._client.api.get_playlist(playlist_id)
        else:
            raw = self._client.api.get_playlist(playlist_id, limit)

        pl = c.structure(raw, models.Playlist)
        results = [self._convert_track(t) for t in pl.tracks]
        return TrackList(title=None, type=TrackList.type_ordered(), tracks=results)

    def search_tracks(self, query: str, limit: int = 5) -> TrackList:
        raw = self._client.api.search(
            query=query, filter="songs", limit=limit, ignore_spelling=False
        )
        ts = c.structure(raw, list[models.Track])
        results = [self._convert_track(t) for t in ts]
        return TrackList(title=None, type=TrackList.type_ordered(), tracks=results)

    def update_playlist_tracks(
        self, playlist_id: str, new_tracks: list[Track], old_tracks: list[Track]
    ) -> bool:
        logger.info("Update youtube music playlist tracks.")

        if old_tracks:
            result = self._client.api.remove_playlist_items(
                playlist_id,
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

        try:
            result = self._client.api.add_playlist_items(
                playlist_id,
                [t.raw.videoId for t in new_tracks],
                source_playlist=None,
                duplicates=False,
            )
            if "status" not in result or result.get("status") != "STATUS_SUCCEEDED":
                return False
            return True
        except YTMusicServerError:
            logger.exception("YouTube Music error.")
            return False

    def update_playlist_details(
        self, playlist_id: str, title: str, description: str, is_public: bool
    ):
        logger.info("Update youtube music playlist details.")

        result = self._client.api.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus="PUBLIC" if is_public else "PRIVATE",
        )
        return result == "STATUS_SUCCEEDED"

    def _convert_track(self, item: models.Track):
        return Track(
            title=item.title,
            artists=[a.name for a in item.artists],
            origin_code=self.code,
            raw=item,
        )
