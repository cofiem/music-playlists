import logging
from typing import Optional

from music_playlists.downloader import Downloader
from music_playlists.intermediate.track import Track as ImmTrack
from music_playlists.intermediate.track_list import TrackList
from music_playlists.youtube_music.client import Client
from music_playlists.youtube_music.playlist import Playlist
from music_playlists.youtube_music.track import Track


class Manage:

    code = "youtube-music"

    _logger = logging.getLogger(code)

    def __init__(self, downloader: Downloader, client: Client):
        self._downloader = downloader
        self._client = client
        self._session = self._downloader.get_session

    @property
    def client(self):
        return self._client

    def playlist_tracks(
        self, playlist_id: str, limit: Optional[int] = 100
    ) -> TrackList:
        self._logger.info("Get playlist tracks from youtube music.")

        if limit is None:
            raw = self._client.api.get_playlist(playlist_id)
        else:
            raw = self._client.api.get_playlist(playlist_id, limit)

        pl = Playlist.from_dict(raw)
        results = [self._convert_track(t) for t in pl.tracks]
        return TrackList(title=None, type=TrackList.type_ordered(), tracks=results)

    def search_tracks(self, query: str, limit: int = 5) -> TrackList:
        raw = self._client.api.search(
            query=query, filter="songs", limit=limit, ignore_spelling=False
        )
        ts = Track.schema().load(raw, many=True)
        results = [self._convert_track(t) for t in ts]
        return TrackList(title=None, type=TrackList.type_ordered(), tracks=results)

    def update_playlist_tracks(
        self, playlist_id: str, new_tracks: list[ImmTrack], old_tracks: list[ImmTrack]
    ) -> bool:
        self._logger.info("Update youtube music playlist tracks.")

        if old_tracks:
            result = self._client.api.remove_playlist_items(
                playlist_id,
                [
                    {
                        "videoId": t.raw.video_id,
                        "setVideoId": t.raw.set_video_id,
                    }
                    for t in old_tracks
                ],
            )

            if result != "STATUS_SUCCEEDED":
                return False

        result = self._client.api.add_playlist_items(
            playlist_id,
            [t.raw.video_id for t in new_tracks],
            source_playlist=None,
            duplicates=False,
        )
        if "status" not in result or result.get("status") != "STATUS_SUCCEEDED":
            return False
        return True

    def update_playlist_details(
        self, playlist_id: str, title: str, description: str, is_public: bool
    ):
        self._logger.info("Update youtube music playlist details.")

        result = self._client.api.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus="PUBLIC" if is_public else "PRIVATE",
        )
        return result == "STATUS_SUCCEEDED"

    def _convert_track(self, item: Track):
        return ImmTrack(
            title=item.title,
            artists=[a.name for a in item.artists],
            origin_code=self.code,
            raw=item,
        )
