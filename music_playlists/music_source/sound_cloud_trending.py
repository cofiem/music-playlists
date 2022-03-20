# import logging
# from typing import List, Optional
# from urllib.parse import urlencode
#
# from music_playlists.downloader import Downloader
# from music_playlists.music_source.source_playlist import SourcePlaylist
# from music_playlists.track import Track

#
# class SoundCloudTrending(SourcePlaylist):
#     code = "soundcloud_trending_weekly_au"
#     title = "SoundCloud Trending Australia Weekly"
#
#     def __init__(self, logger: logging.Logger, downloader: Downloader, client_id: str):
#         self._logger = logger
#         self._downloader = downloader
#         self._client_id = client_id
#
#         self._url = "https://api-v2.soundcloud.com/charts?{qs}"
#
#     def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
#         self._logger.info(f"Started {self.title}.")
#
#         # get content
#         url = self.build_url(client_id=self._client_id)
#
#         # download track list
#         cache_name = self._downloader.cache_temp
#         tracks_data = self._downloader.download_json(cache_name, url) or {}
#
#         result = []
#         for index, item in enumerate(tracks_data.get("collection", [])):
#             track_title = item["track"]["title"]
#             publisher_metadata = item["track"].get("publisher_metadata")
#             if publisher_metadata and publisher_metadata.get("artist"):
#                 artist = publisher_metadata.get("artist")
#             elif "-" in track_title:
#                 track_title_split = track_title.split("-")
#                 artist = track_title_split[-1]
#                 track_title = " ".join(track_title_split[0:-1])
#             elif item["track"]["user"]["full_name"]:
#                 artist = item["track"]["user"]["full_name"]
#             elif item["track"]["user"]["username"]:
#                 artist = item["track"]["user"]["username"]
#             else:
#                 artist = ""
#
#             result.append(
#                 Track.create(
#                     self.code,
#                     item["track"].get("id"),
#                     track_title.strip(),
#                     [artist.strip()],
#                     item,
#                 )
#             )
#
#         self._logger.info(f"Completed {self.title} with {len(result)} tracks.")
#         if limit is not None and 0 < limit < len(result):
#             result = result[:limit]
#         return result
#
#     def build_url(
#         self,
#         client_id: str,
#         kind: str = "trending",
#         genre: str = "soundcloud:genres:all-music",
#         region: str = "soundcloud:regions:AU",
#         high_tier_only: bool = False,
#         limit: str = "50",
#         offset: str = "0",
#         linked_partitioning: str = "1",
#         app_locale: str = "en",
#     ):
#         qs = urlencode(
#             {
#                 "client_id": client_id,
#                 "kind": kind,
#                 "genre": genre,
#                 "region": region,
#                 "high_tier_only": str(high_tier_only).lower(),
#                 "limit": limit,
#                 "offset": offset,
#                 "linked_partitioning": linked_partitioning,
#                 "app_locale": app_locale,
#             }
#         )
#         url = self._url.format(qs=qs)
#         return url
