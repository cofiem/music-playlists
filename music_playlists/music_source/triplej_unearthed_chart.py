import logging
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

from music_playlists.downloader import Downloader
from music_playlists.music_source.source_playlist import SourcePlaylist
from music_playlists.track import Track


class TripleJUnearthedChart(SourcePlaylist):
    code = "triple_j_unearthed_chart"
    title = "Triple J Unearthed Weekly"

    def __init__(
        self, logger: logging.Logger, downloader: Downloader, time_zone: datetime.tzinfo
    ):
        self._logger = logger
        self._downloader = downloader

        # https://music.abcradio.net.au/api/v1/recordings/plays.json?order=desc&limit=50&service=unearthed&from=2019-11-12T13:00:00Z&to=2019-11-19T13:00:00Z
        self._url = "https://music.abcradio.net.au/api/v1/recordings/plays.json?{qs}"
        self._time_zone = time_zone

    def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
        # build dates for urls
        current_time = datetime.now(tz=self._time_zone)
        current_day = current_time.date()

        url = self.build_url(
            "unearthed",
            date_from=current_day - timedelta(days=8),
            date_to=current_day - timedelta(days=1),
        )

        # download track list
        tracks_data = self._downloader.download_json(
            self._downloader.cache_persisted, url
        )

        result = []
        for index, item in enumerate(tracks_data["items"]):
            title = item["title"]
            track_id = item["arid"]
            original_artists = item["artists"]

            # get primary artist and featured artists
            artist = ""
            featuring = ""
            for raw_artist in original_artists:
                if raw_artist["type"] == "primary":
                    artist = f'{artist}, {raw_artist["name"]}'
                elif raw_artist["type"] == "featured":
                    featuring = f'{artist}, {raw_artist["name"]}'
                else:
                    raise Exception(
                        f"Unrecognised artist {raw_artist['type']}, {artist}, {raw_artist['name']}."
                    )

            artists = [artist.strip(", ")]
            for i in featuring.split(", "):
                featured = i.strip(", ")
                if featured and featured not in artists:
                    artists.append(featured)

            # build track
            result.append(
                Track.create(
                    self.code,
                    track_id,
                    title,
                    artists,
                    {
                        "artists": artists,
                        "source_id": track_id,
                        "source_order": index + 1,
                        "original_track": title,
                        "original_artists": original_artists,
                    },
                )
            )

        self._logger.info(f"Retrieved {self.title} with {len(result)} tracks.")

        if limit is not None and 0 < limit < len(result):
            result = result[:limit]

        return result

    def build_url(self, service, date_from, date_to, order="desc", limit="50"):
        qs = urlencode(
            {
                "order": order,
                "limit": limit,
                "service": service,
                "from": f"{date_from.strftime('%Y-%m-%d')}T13:00:00Z",
                "to": f"{date_to.strftime('%Y-%m-%d')}T13:00:00Z",
            }
        )
        url = self._url.format(qs=qs)
        return url
