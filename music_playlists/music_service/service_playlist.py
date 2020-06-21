import logging
import os
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from time import sleep
from typing import List, TYPE_CHECKING

from dataclasses_json import dataclass_json

if TYPE_CHECKING:
    from music_playlists.data.track import Track


@dataclass_json
@dataclass
class ServicePlaylist:
    """An ordered list of tracks from a streaming music service."""
    playlist_name: str

    service_name: str
    service_playlist_env_var: str

    playlist_description: str = field(default=None)
    playlist_title: str = field(default=None)
    service_playlist_code: str = field(default=None)

    tracks: List['Track'] = field(default_factory=list)
    tracks_missing: int = field(default=0)
    tracks_included: int = field(default=0)
    tracks_total: int = field(default=0)
    tracks_new: int = field(default=0)
    tracks_removed: int = field(default=0)
    tracks_up: int = field(default=0)
    tracks_down: int = field(default=0)

    def __post_init__(self):
        """"""
        self._logger = logging.getLogger(__name__)
        if not self.service_playlist_code and self.service_playlist_env_var:
            self.service_playlist_code = os.getenv(self.service_playlist_env_var)

    def populate_tracks(self, source_tracks: List['Track'], service_tracks: List['Track'],
                        query_track, time_zone: datetime.tzinfo) -> None:
        self.tracks = []
        self.tracks_missing = 0
        self.tracks_included = 0
        self.tracks_total = 0
        self.tracks_new = 0
        self.tracks_removed = 0
        self.tracks_up = 0
        self.tracks_down = 0

        used_cache = False
        for source_track in source_tracks:
            found_track = None

            for service_track in service_tracks:
                if source_track.is_match(service_track):
                    found_track = service_track
                    used_cache = False
                    break

            if not found_track:
                if not used_cache:
                    sleep(1)
                used_cache, available_tracks = query_track(source_track)
                for available_track in available_tracks:
                    if source_track.is_match(available_track):
                        found_track = available_track
                        break
                if not found_track:
                    available_display = ', '.join(str(i) for i in available_tracks)
                    self._logger.warning(f"Did not select a song for '{str(source_track)}' "
                                         f"from {len(available_tracks)} "
                                         f"options: '{available_display}'")

            if found_track:
                self.tracks.append(found_track)
                self.tracks_included += 1
            else:
                self.tracks_missing += 1

        # update the new playlist changes and set description
        self.tracks_total = self.tracks_included + self.tracks_missing
        old_ids = [i.track_id for i in service_tracks]
        new_ids = [i.track_id for i in self.tracks]

        for old_index, old_id in enumerate(old_ids):
            try:
                new_index = new_ids.index(old_id)
            except ValueError:
                new_index = None

            if not new_index:
                self.tracks_removed += 1
            elif new_index and new_index < old_index:
                self.tracks_up += 1
            elif new_index and new_index > old_index:
                self.tracks_down += 1

        for new_index, new_id in enumerate(new_ids):
            try:
                old_index = old_ids.index(new_id)
            except ValueError:
                old_index = None

            if not old_index:
                self.tracks_new += 1

        tracks_percent = float(self.tracks_included) / float(self.tracks_total + 0.000001)
        self.playlist_description = ' '.join([
            f"This playlist is generated each day.",
            f"There are {self.tracks_included} songs of {self.tracks_total} ({tracks_percent:.0%}).",
            f"Couldn't find {self.tracks_missing} songs.",
            "For more information: https://github.com/cofiem/music-playlists"
        ])
        current_datetime = datetime.now(tz=time_zone)
        self.playlist_title = f"{self.playlist_name} ({current_datetime.strftime('%a, %d %b %Y')})"
