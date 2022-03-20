import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional

from boltons.strutils import slugify

from music_playlists.downloader import Downloader
from music_playlists.music_source.source_playlist import SourcePlaylist
from music_playlists.track import Track


class Radio4zzzMostPlayed(SourcePlaylist):
    code = "radio_4zzz_most_played"
    title = "4zzz Most Played Weekly"

    def __init__(
        self, logger: logging.Logger, downloader: Downloader, time_zone: datetime.tzinfo
    ):
        self._logger = logger
        self._downloader = downloader
        self._url = "https://airnet.org.au/rest/stations/4ZZZ/programs"
        self._time_zone = time_zone

    def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
        cache_temp = self._downloader.cache_temp
        cache_pers = self._downloader.cache_persisted
        # build dates for urls
        current_time = datetime.now(tz=self._time_zone)
        date_from = current_time - timedelta(days=7)
        date_to = current_time

        # download 4zzz programs
        programs = self._downloader.download_json(self._url)

        tracks = {}

        # programs
        for program in programs:
            if program.get("archived"):
                continue
            program_name = program["name"]

            # episodes
            episodes_url = f"{program['programRestUrl']}/episodes"
            episodes = self._downloader.download_json(episodes_url) or []
            pat = "%Y-%m-%d %H:%M:%S"
            for episode in episodes:
                episode_start = datetime.strptime(episode["start"], pat)
                episode_start = episode_start.replace(tzinfo=self._time_zone)
                episode_end = datetime.strptime(episode["end"], pat)
                episode_end = episode_end.replace(tzinfo=self._time_zone)

                # must be fully inside the from -> to dates
                if episode_start < date_from or episode_end > date_to:
                    continue

                # playlist tracks
                playlist_url = f"{episode['episodeRestUrl']}/playlists"
                playlist_raw = self._downloader.download_json(playlist_url)
                for track in playlist_raw or []:
                    track_type = track["type"]
                    track_artist = track["artist"]
                    track_title = track["title"]
                    track_track = track["track"]

                    if track_type != "track":
                        raise Exception(
                            f"Track type is expected to be 'track', but is {track_type}."
                        )

                    if track_title != track_track:
                        raise Exception(
                            f"Title and track are expected to match, but do not: '{track_title}' != '{track_track}'"
                        )

                    track_key = "-".join(
                        [
                            slugify(track_artist, delim="-", ascii=True).decode(
                                "utf-8"
                            ),
                            slugify(track_track, delim="-", ascii=True).decode("utf-8"),
                        ]
                    )

                    item = {
                        "type": track_type,
                        "id": track["id"],
                        "artist": track_artist,
                        "title": track_title,
                        "track": track_track,
                        "release": track["release"],
                        "time": track["time"],
                        "notes": track["notes"],
                        "twitter": track["twitterHandle"],
                        "is_australian": track["contentDescriptors"]["isAustralian"],
                        "is_local": track["contentDescriptors"]["isLocal"],
                        "is_female": track["contentDescriptors"]["isFemale"],
                        "is_indigenous": track["contentDescriptors"]["isIndigenous"],
                        "is_new": track["contentDescriptors"]["isNew"],
                        "wikipedia": track["wikipedia"],
                        "image": track["image"],
                        "video": track["video"],
                        "url": track["url"],
                        "approximate_time": track["approximateTime"],
                        "program_name": program_name,
                        "episode_start": episode_start,
                    }

                    if track_key in tracks:
                        tracks[track_key].append(item)
                    else:
                        tracks[track_key] = [item]

        # find the top 50 most played tracks
        most_played_tracks = sorted(
            [(len(v), k, v) for k, v in tracks.items() if len(v) > 1], reverse=True
        )[:100]

        # build the source playlist tracks
        result = []
        for index, most_played_track in enumerate(most_played_tracks):
            play_count = most_played_track[0]
            track_id = most_played_track[1]
            track_info = most_played_track[2]

            info = self._build_info(track_id, play_count, track_info)

            title = info.get("title")
            artists = [info.get("artist")]
            result.append(Track.create(self.code, track_id, title, artists, info))

        self._logger.info(f"Retrieved {self.title} with {len(result)} tracks.")
        if limit is not None and 0 < limit < len(result):
            result = result[:limit]
        return result

    def _build_info(self, track_id, play_count, track_info):
        return {
            "title": self._choose_value([i["track"] for i in track_info]),
            "artist": self._choose_value([i["artist"] for i in track_info]),
            "play_count": play_count,
            "source_id": track_id,
            "is_australian": self._choose_value(
                [i["is_australian"] for i in track_info]
            ),
            "is_local": self._choose_value([i["is_local"] for i in track_info]),
            "is_female": self._choose_value([i["is_female"] for i in track_info]),
            "is_indigenous": self._choose_value(
                [i["is_indigenous"] for i in track_info]
            ),
            "is_new": self._choose_value([i["is_new"] for i in track_info]),
            "releases": {i["release"] for i in track_info if i["release"]} or None,
            "notes": {i["notes"] for i in track_info if i["notes"]} or None,
            "twitters": {i["twitter"] for i in track_info if i["twitter"]} or None,
            "wikipedias": {i["wikipedia"] for i in track_info if i["wikipedia"]}
            or None,
            "images": {i["image"] for i in track_info if i["image"]} or None,
            "videos": {i["video"] for i in track_info if i["video"]} or None,
            "urls": {i["url"] for i in track_info if i["url"]} or None,
            "program_names": {
                i["program_name"] for i in track_info if i["program_name"]
            }
            or None,
        }

    def _choose_value(self, values: List[Any]) -> Any:
        gathered = {}
        for value in values:
            if value is None:
                continue
            if value not in gathered:
                gathered[value] = 1
            else:
                gathered[value] += 1
        values_sorted = sorted([(v, k) for k, v in gathered.items()], reverse=True)
        return values_sorted[0][1] if values_sorted else None
