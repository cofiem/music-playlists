import logging

from datetime import tzinfo

import attrs
import requests

from beartype import beartype
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override

from music_playlists import intermediate as inter
from music_playlists import model, utils


logger = logging.getLogger(__name__)


@beartype
@attrs.frozen
class Artist:
    name: str
    url: str
    mbid: str | None = None


utils.c.register_unstructure_hook(
    Artist,
    make_dict_unstructure_fn(
        Artist, utils.c, _cattrs_omit_if_default=True, attr=override(rename="@attr")
    ),
)
utils.c.register_structure_hook(
    Artist,
    make_dict_structure_fn(Artist, utils.c, attr=override(rename="@attr")),
)


@beartype
@attrs.frozen
class Image:
    text: str
    size: str


utils.c.register_unstructure_hook(
    Image,
    make_dict_unstructure_fn(Image, utils.c, text=override(rename="#text")),
)
utils.c.register_structure_hook(
    Image,
    make_dict_structure_fn(Image, utils.c, text=override(rename="#text")),
)


@beartype
@attrs.frozen
class Streamable:
    text: str
    fulltrack: str


utils.c.register_unstructure_hook(
    Streamable,
    make_dict_unstructure_fn(Streamable, utils.c, text=override(rename="#text")),
)
utils.c.register_structure_hook(
    Streamable,
    make_dict_structure_fn(Streamable, utils.c, text=override(rename="#text")),
)


@beartype
@attrs.frozen
class TrackAttr:
    rank: str


@beartype
@attrs.frozen
class Track:
    name: str
    duration: str
    listeners: str
    url: str
    streamable: Streamable
    artist: Artist
    image: list[Image]
    attr: TrackAttr
    mbid: str | None = None


utils.c.register_unstructure_hook(
    Track,
    make_dict_unstructure_fn(
        Track, utils.c, _cattrs_omit_if_default=True, attr=override(rename="@attr")
    ),
)
utils.c.register_structure_hook(
    Track,
    make_dict_structure_fn(Track, utils.c, attr=override(rename="@attr")),
)


@beartype
class Manage(model.Source):
    code = "last-fm"

    @classmethod
    def available(cls):
        return {
            "aus-most-played-weekly": cls.aus_top_tracks,
        }

    def __init__(self, downloader: utils.Downloader, time_zone: tzinfo, api_key: str):
        self._dl = downloader
        self._tz = time_zone
        self._api_key = api_key
        self._url = "https://ws.audioscrobbler.com/2.0"

    def aus_top_tracks(self, title: str, refresh=False) -> inter.TrackList:
        logger.info("Get %s.", title)

        country = "australia"

        top = self.top_tracks(country, refresh=refresh)
        results = [
            inter.Track(
                origin_code=self.code,
                track_id=t.mbid,
                title=t.name,
                artists=[t.artist.name],
                raw=t,
            )
            for t in top
        ]
        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=results,
        )
        return tl

    def top_tracks(
        self,
        country: str,
        output_format: str = "json",
        limit: bool = "50",
        page: str = "1",
        refresh=False,
    ) -> list[Track]:
        params = {
            "api_key": self._api_key,
            "method": "geo.gettoptracks",
            "country": country,
            "format": output_format,
            "limit": limit,
            "page": page,
        }
        r = self._dl.get_session.get(self._url, params=params, refresh=refresh)
        if r.status_code == requests.codes.ok and r.text:
            return utils.c.structure(r.json()["tracks"]["track"], list[Track])
        raise ValueError(str(r))
