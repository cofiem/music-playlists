from datetime import datetime
from time import sleep
from typing import List, Optional

from boltons.strutils import slugify

from music_playlists.track import Track


class ServicePlaylist:
    """Manages tracks in service playlists."""

    code = None

    def get_playlist_tracks(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> List[Track]:
        """
        Get the tracks in the service playlist.

        :param playlist_id: The playlist id in the service.
        :param limit: The maximum number of tracks.
        """
        raise NotImplementedError()

    def set_playlist_tracks(
        self, playlist_id: str, new_tracks: List[Track], old_tracks: List[Track]
    ) -> bool:
        """
        Set the tracks in the service playlist.

        This will replace any tracks currently in the playlist.
        :param playlist_id:  The playlist id in the service.
        :param new_tracks: The tracks to set in the playlist.
        :param old_tracks: The tracks previously in the playlist.
        """
        raise NotImplementedError()

    def set_playlist_details(
        self,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        """
        Update the playlist details.

        :param playlist_id:  The playlist id in the service.
        :param title: The title of the playlist.
        :param description: The description for the playlist.
        :param is_public: Whether the playlist if public or not.
        """
        raise NotImplementedError()

    def find_track(self, query: str, limit: int = 5) -> tuple[bool, list[Track]]:
        """
        Find tracks in a service matching a query.

        :param query: The search text.
        :param limit: The maximum number of results.
        """
        raise NotImplementedError()

    def is_match(self, query_track: Track, result_track: Track) -> bool:
        query_new = Track.create(
            query_track.origin_code,
            query_track.track_id,
            query_track.title,
            query_track.artists,
            query_track.info,
        )
        query_title = slugify(query_new.title)
        query_artist = slugify(query_new.artists[0])
        query_featured = slugify(", ".join(query_new.artists[1:]))

        result_new = Track.create(
            result_track.origin_code,
            result_track.track_id,
            result_track.title,
            result_track.artists,
            result_track.info,
        )
        result_title = slugify(result_new.title)
        result_artist = slugify(result_new.artists[0])
        result_featured = slugify(", ".join(result_new.artists[1:]))

        match_title = query_title in result_title
        # match_artist = query_artist in result_artist
        match_featuring = query_featured in result_featured
        match_featuring2 = result_featured in query_featured

        equal_title = query_title == result_title
        equal_artist = query_artist == result_artist
        # equal_featuring = query_featured == result_featured

        has_featuring = query_featured and result_featured

        # these are the variations that are valid
        if equal_title and equal_artist and match_featuring and has_featuring:
            return True
        if match_title and equal_artist and match_featuring and not has_featuring:
            return True
        if (
            equal_title
            and equal_artist
            and has_featuring
            and (match_featuring or match_featuring2)
        ):
            return True

        return False

    def build_new_playlist(
        self,
        tracks_current: List[Track],
        tracks_new: List[Track],
        time_zone: datetime.tzinfo,
    ):
        tracks_add = []

        tracks_missing = 0
        tracks_included = 0
        tracks_total = 0
        tracks_added = 0
        tracks_removed = 0
        tracks_up = 0
        tracks_down = 0

        for source_track in tracks_new:
            found_track = None

            for service_track in tracks_current:
                if self.is_match(source_track, service_track):
                    found_track = service_track
                    break

            if not found_track:
                available_tracks = []
                for query_string in source_track.query_strings:
                    used_cache, current_available_tracks = self.find_track(query_string)
                    if not used_cache:
                        # sleep for 1 second so the find track http requests are not too fast
                        sleep(1)
                    available_tracks.extend(current_available_tracks)
                    for available_track in current_available_tracks:
                        if self.is_match(source_track, available_track):
                            found_track = available_track
                            break

                if not found_track:
                    available_display = ", ".join(str(i) for i in available_tracks)
                    self._logger.warning(
                        f"Did not select a song for queries '{'; '.join(source_track.query_strings)}' "
                        f"from {len(available_tracks)} "
                        f"options: '{available_display}'"
                    )

            if found_track:
                tracks_add.append(found_track)
                tracks_included += 1
            else:
                tracks_missing += 1

        # update the new playlist changes and set description
        tracks_total = tracks_included + tracks_missing
        old_ids = [i.track_id for i in tracks_current]
        new_ids = [i.track_id for i in tracks_add]

        for old_index, old_id in enumerate(old_ids):
            try:
                new_index = new_ids.index(old_id)
            except ValueError:
                new_index = None

            if not new_index:
                tracks_removed += 1
            elif new_index and new_index < old_index:
                tracks_up += 1
            elif new_index and new_index > old_index:
                tracks_down += 1

        for new_index, new_id in enumerate(new_ids):
            try:
                old_index = old_ids.index(new_id)
            except ValueError:
                old_index = None

            if not old_index:
                tracks_added += 1

        tracks_percent = float(tracks_included) / float(tracks_total + 0.000001)
        current_datetime = datetime.now(tz=time_zone)
        playlist_description = " ".join(
            [
                f"This playlist was generated on {current_datetime.strftime('%a, %d %b %Y')}.",
                f"Found {tracks_included} of {tracks_total} songs ({tracks_percent:.0%}) "
                "from the source playlist.",
                "For more information: https://github.com/cofiem/music-playlists",
            ]
        )

        return tracks_add, playlist_description
