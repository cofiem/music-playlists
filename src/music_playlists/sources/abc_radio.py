import datetime
import logging

import attrs
import beartype
import requests
from cattrs.gen import make_dict_structure_fn, override

from music_playlists import intermediate as inter
from music_playlists import model, utils

logger = logging.getLogger(__name__)


@beartype.beartype
@attrs.frozen
class CoreNextApiItemImage:
    imgSrc: str
    ratio: str
    alt: str
    srcSet: list


@beartype.beartype
@attrs.frozen
class CoreNextApiItem:
    id: str
    title: str
    artist: str
    hasComposerLabel: bool
    duration: int
    cardImageFallbackType: str
    expandedTitle: str
    primaryPerformer: str
    timestampType: str
    timestampRelativeSR: str
    isAustralian: bool
    youTubeUrl: str| None = None
    spotifyUrl: str| None = None
    appleUrl: str| None = None
    unearthedUrl: str | None = None
    cardImageProps: CoreNextApiItemImage | None = None
    release: str | None = None
    label: str | None = None
    year: str | None = None


@beartype.beartype
@attrs.frozen
class CoreNextApiPagination:
    offset: int
    total: int
    size: int


@beartype.beartype
@attrs.frozen
class CoreNextApiResult:
    items: list[CoreNextApiItem]
    pagination: CoreNextApiPagination
    station: str
    date_from: str
    date_to: str


utils.c.register_structure_hook(
    CoreNextApiResult,
    make_dict_structure_fn(
        CoreNextApiResult,
        utils.c,
        date_from=override(rename="from"),
        date_to=override(rename="to")
    ),
)


@beartype.beartype
class Manage(model.Source):
    code = "abc-radio"

    @classmethod
    def available(cls):
        return {
            "doublej-most-played-weekly": cls.doublej_most_played,
            "triplej-most-played-weekly": cls.triplej_most_played,
            "unearthed-most-played-weekly": cls.unearthed_most_played,
            "jazz-most-played-weekly": cls.jazz_most_played,
            "classic-most-played-weekly": cls.classic_most_played,
        }

    def __init__(self, downloader: utils.Downloader, time_zone):
        self._dl = downloader
        self._tz = time_zone
        self._url_core_next_most_played = "https://www.abc.net.au/core-next/api/mostPlayed"
        # TODO: consider whether tracklist is useful in addition to most played
        # self._url_core_next_tracklist = "https://www.abc.net.au/core-next/api/tracklist"

    def triplej_most_played(self, title: str) -> inter.TrackList:
        return self._tracks_most_played(title, "TRIPLEJ")

    def doublej_most_played(self, title: str) -> inter.TrackList:
        return self._tracks_most_played(title, "DOUBLEJ")

    def unearthed_most_played(self, title: str) -> inter.TrackList:
        return self._tracks_most_played(title, "UNEARTHED")

    def classic_most_played(self, title: str) -> inter.TrackList:
        return self._tracks_most_played(title, "CLASSIC")

    def jazz_most_played(self, title: str) -> inter.TrackList:
        return self._tracks_most_played(title, "JAZZ")

    def _tracks_most_played(self, title: str, station: str):
        logger.info("Get %s.", title)

        current_time = datetime.datetime.now(tz=self._tz)
        current_day = current_time.date()

        date_from = current_day - datetime.timedelta(days=8)
        date_to = current_day - datetime.timedelta(days=1)

        results = []
        size = 20
        offset = 0
        item_cap = 100
        while True:
            result = self._api_most_played(
                station=station,
                date_from=date_from,
                date_to=date_to,
                size=size,
                offset=offset,
                item_cap=item_cap,
            )
            results.extend([inter.Track(
                origin_code=self.code,
                track_id=p.id,
                title=p.title,
                artists=list({p.artist, p.primaryPerformer}),
                raw=p,
            ) for p in result.items])
            count = result.pagination.offset + len(result.items)
            if count < item_cap:
                offset += size
            else:
                break

        tl = inter.TrackList(
            title=title,
            type=inter.TrackListType.ORDERED,
            tracks=results,
        )
        return tl

    def _api_most_played(
            self,
            station: str,
            date_from: datetime.date,
            date_to: datetime.date,
            size: int = 50,
            offset: int = 0,
            item_cap: int = 50,
            tz: str | None = None
    ):
        params = {
            "station": station,
            "from": f"{date_from.strftime('%Y-%m-%d')}T14:00:00+00:00",
            "to": f"{date_to.strftime('%Y-%m-%d')}T14:00:00+00:00",
            "size": size,
            "offset": offset,
            "item_cap": item_cap,
        }
        if tz:
            params['tz'] = tz
        r = self._dl.get(
            self._url_core_next_most_played, params=params
        )
        if r.status_code == requests.codes.ok and r.text:
            data = r.json()
            return utils.c.structure(data, CoreNextApiResult)
        raise ValueError(str(r))
