import datetime
import logging
import pathlib
import zoneinfo

from beartype import beartype
from beartype.claw import beartype_package

from music_playlists import intermediate as inter
from music_playlists import model, settings, utils
from music_playlists.intermediate import TrackListType
from music_playlists.services import spotify, youtube_music
from music_playlists.sources import abc_radio, last_fm, radio_4zzz


beartype_package("music_playlists")
logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("requests_cache").setLevel(logging.INFO)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)


logger = logging.getLogger(__name__)


@beartype
class Process:
    def __init__(self, config_file: pathlib.Path):
        # common
        self._settings = settings.Settings(config_file)
        s = self._settings

        self._time_zone = zoneinfo.ZoneInfo(s.time_zone)
        tz = self._time_zone

        self._base_path = pathlib.Path(s.base_path).resolve() if s.base_path else None
        self._downloader = utils.Downloader(store_path=self._base_path)
        d = self._downloader

        # sources
        self._abc_radio = abc_radio.Manage(d, tz)
        self._last_fm = last_fm.Manage(d, tz, s.lastfm_api_key)
        self._radio_4zzz = radio_4zzz.Manage(d, tz)

        # services
        self._spotify_client = spotify.Client(
            d,
            s.spotify_redirect_uri,
            s.spotify_client_id,
            s.spotify_client_secret,
            s.spotify_refresh_token,
        )
        self._spotify = spotify.Manage(d, self._spotify_client)

        self._youtube_music_client = youtube_music.Client(d, s.youtube_music_config)
        self._youtube_music = youtube_music.Manage(d, self._youtube_music_client)

        # processing
        self._intermediate = inter.Manage()
        self._playlists_config = list(self._settings.playlists)

        self._sources: list[model.Source] = [
            self._abc_radio,
            self._last_fm,
            self._radio_4zzz,
        ]

    def list_available(self):
        result = []
        for item in self._sources:
            available = item.available() or {}
            for code in available.keys():
                for pc in self._playlists_config:
                    if pc.code == code and pc.source == item.code:
                        result.append(
                            {
                                "code": code,
                                "title": pc.title,
                                "source": pc.source,
                                "service": pc.service,
                                "playlist_id": pc.playlist_id,
                            }
                        )
        result = sorted(
            result,
            key=lambda key: (key.get("source"), key.get("code"), key.get("service")),
        )
        return result

    def source_show(self, name: str, refresh: bool = False):
        for item in self._sources:
            available = item.available() or {}
            for code in available.keys():
                key = f"{item.code}-{code}"
                if name != key:
                    continue
                for pc in self._playlists_config:
                    if pc.code == code and pc.source == item.code:
                        func = available[code]
                        tracks = func(item, pc.title, refresh)
                        if tracks.type == TrackListType.ALL_PLAYS:
                            tracks = self._intermediate.most_played(tracks)
                        return tracks
        raise ValueError(f"Could not find a source named '{name}'.")

    def services_update(
        self,
        code_name: str | None = None,
        source_name: str | None = None,
        service_name: str | None = None,
        refresh: bool = False,
    ):
        logger.info(
            "Updating music playlists with code %s, source %s, service %s.",
            code_name or "(all)",
            source_name or "(all)",
            service_name or "(all)",
        )

        if not service_name or service_name == self._spotify.code:
            self._spotify.client.login()
        if not service_name or service_name == self._youtube_music.code:
            self._youtube_music.client.login()

        # get the new tracks from the source playlists
        # and find the new tracks in the streaming services
        for source in self._sources:
            if source_name and source_name != source.code:
                continue
            available = source.available() or {}
            for code in available.keys():
                code_key = f"{source.code}-{code}"
                if code_name and code_name != code_key:
                    continue
                for pc in self._playlists_config:
                    if not pc.playlist_id:
                        continue
                    if service_name and service_name != pc.service:
                        continue
                    if pc.code == code and pc.source == source.code:
                        func = available[code]
                        tracks = func(source, pc.title, refresh)
                        if tracks.type == TrackListType.ALL_PLAYS:
                            tracks = self._intermediate.most_played(tracks)
                        self._intermediate.normalise_tracklist(tracks)
                        if pc.service == self._spotify.code:
                            self.update_spotify(tracks, pc.playlist_id)
                        elif pc.service == self._youtube_music.code:
                            self.update_youtube_music(tracks, pc.playlist_id)

        logger.info("Finished updating music playlists")

    def update_spotify(self, track_list: inter.TrackList, playlist_id: str):
        return self._update_service(
            "Spotify",
            track_list,
            playlist_id,
            inter.ServiceConfig(
                track_search=self._spotify.search_tracks,
                track_embedded_id=self._spotify.track_embedded_id,
                playlist_tracks=self._spotify.update_playlist_tracks,
                playlist_info=self._spotify.update_playlist_details,
            ),
        )

    def update_youtube_music(self, track_list: inter.TrackList, playlist_id: str):
        return self._update_service(
            "YouTube Music",
            track_list,
            playlist_id,
            inter.ServiceConfig(
                track_search=self._youtube_music.search_tracks,
                track_embedded_id=self._youtube_music.track_embedded_id,
                playlist_tracks=self._youtube_music.update_playlist_tracks,
                playlist_info=self._youtube_music.update_playlist_details,
            ),
        )

    def _find_tracks(
        self, service_name: str, tracks: list[inter.Track], search_func, embedded_func
    ):
        embedded_query = "___EMBEDDED_QUERY___"

        first_count = 5
        total_count = 0
        found_count = 0
        results = {}
        for track in tracks:
            total_count += 1
            query_match = None

            # Check the track to see if it already has an id from the service.
            embedded = embedded_func(track)
            if embedded is not None:
                results[embedded_query] = embedded
                query_match = embedded_query

            # Query the service to find the track.
            if embedded is None:
                queries = self._intermediate.queries(track)
                service_found_count = 0
                for query in queries:
                    if query in results:
                        query_match = query
                        break
                    found_tracks = search_func(query)
                    service_found_count += len(found_tracks.tracks)
                    match = self._intermediate.match(
                        track, found_tracks.tracks, first_count
                    )
                    if match:
                        results[query] = match
                        query_match = query
                        break

                if query_match:
                    found_count += 1
                else:
                    logger.warning(
                        "No match for track %s in first %s %s service tracks for %s queries %s.",
                        track,
                        min(service_found_count, first_count),
                        service_name,
                        len(queries),
                        queries,
                    )

        tracks_percent = float(found_count) / float(total_count + 0.000001)
        current_datetime = datetime.datetime.now(tz=self._time_zone)
        found_info = (
            f"Found {found_count} of {total_count} songs ({tracks_percent:.0%})"
        )
        logger.warning(found_info)

        # build text for streaming service playlists
        descr = " ".join(
            [
                "This playlist was generated on "
                f"{current_datetime.strftime('%a, %d %b %Y')}.",
                f"{found_info} from the source playlist.",
                "From: https://github.com/cofiem/music-playlists",
            ],
        )

        return results, descr

    def _update_service(
        self,
        service_name: str,
        track_list: inter.TrackList,
        playlist_id: str,
        service_config: inter.ServiceConfig,
    ):
        sp_tracks, sp_descr = self._find_tracks(
            service_name,
            track_list.tracks,
            service_config.track_search,
            service_config.track_embedded_id,
        )

        playlist_info = inter.ServicePlaylistInfo(
            playlist_id=playlist_id,
            title=track_list.title,
            description=sp_descr,
            is_public=True,
        )
        details_result = service_config.playlist_info(playlist_info)
        logger.info(
            f"Update details {'succeeded' if details_result is True else 'failed'}."
        )

        playlist_tracks = inter.ServicePlaylistTracks(
            playlist_id=playlist_id,
            tracks=[v for k, v in sp_tracks.items()],
        )
        tracks_result = service_config.playlist_tracks(playlist_tracks)
        logger.info(
            f"Update tracks {'succeeded' if tracks_result is True else 'failed'}."
        )
