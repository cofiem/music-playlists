import functools
import logging
import re
import unicodedata

from enum import Enum

import attrs

from beartype import beartype, typing


logger = logging.getLogger(__name__)


@beartype
@attrs.frozen
class TrackNormalised:
    title: str
    artists: list[str]

    @functools.cached_property
    def queries(self) -> list[str]:
        queries = []
        for i in range(len(self.artists), 0, -1):
            queries.append(" ".join([self.title, *self.artists[0:i]]))
        return queries

    def __str__(self):
        t = self.title
        a = "', '".join(a for a in self.artists)
        return f"'{t}' - '{a}'"


@beartype
@attrs.frozen
class Track:
    """A track that may be part of a playlist."""

    origin_code: str
    track_id: str | None
    title: str
    artists: list[str]
    raw: typing.Any
    normalised: TrackNormalised | None = None

    def __str__(self):
        c = self.origin_code
        t = self.title
        a = "', '".join(a for a in self.artists)
        return f"{c}: '{t}' - '{a}'"

    def set_normalised(self, item: TrackNormalised) -> None:
        object.__setattr__(self, "normalised", item)


@beartype
class TrackListType(Enum):
    UNKNOWN = 0

    ORDERED = 1

    ALL_PLAYS = 2


@beartype
@attrs.frozen
class TrackList:
    type: TrackListType
    """The type of track list."""

    title: str | None
    """The title of the set of tracks."""

    tracks: list[Track]
    """The tracks in the list."""


@beartype
@attrs.frozen
class ServicePlaylistTracks:
    playlist_id: str
    tracks: list[Track]


@beartype
@attrs.frozen
class ServicePlaylistInfo:
    playlist_id: str
    title: str
    description: str
    is_public: bool


@beartype
@attrs.frozen
class ServiceConfig:
    track_search: typing.Callable[[str], TrackList]
    track_embedded_id: typing.Callable[[Track], Track | None]
    playlist_tracks: typing.Callable[[ServicePlaylistTracks], bool]
    playlist_info: typing.Callable[[ServicePlaylistInfo], bool]


@beartype
class Manage:
    _title_artist_1 = [
        r"\[",
        r"\]",
        r"\{",
        r"\}",
        r"\(",
        r"\)",
        r"\bft\.\s+",
        r"\bft\b",
        r"\bfeat\.\s+",
        r"\bfeat\b",
        r"\bfeaturing\b",
        r"\bw/\s+",
        r"\bx\b",
        r"\s+&\s+",
        r"\s+\+\s+",
        r"\blive\b\s*\bat\b",
    ]
    _title_artist_2 = [
        r"\bft\.\s+",
        r"\bft\b",
        r"\bfeat\.\s+",
        r"\bfeat\b",
        r"\bfeaturing\b",
        r"\bwith\b",
        r"\bw/\s+",
        r"\bx\b",
        r"\s+&\s+",
        r"\s+\+\s+",
        r"\band\b",
        r"\blive\b\s*\bat\b",
        r"(?:\s+|\b),(?:\s+|\b)",
    ]
    _artist_delimiters = [
        r"\[",
        r"\]",
        r"\{",
        r"\}",
        r"\(",
        r"\)",
        r"\bft\.\s+",
        r"\bft\b",
        r"\bfeat\.\s+",
        r"\bfeat\b",
        r"\bfeaturing\b",
        r"\bwith\b",
        r"\bw/\s+",
        r"\bx\b",
        r"\s+&\s+",
        r"\s+\+\s+",
        r"\band\b",
        r"\blive\b\s*\bat\b",
        r"(?:\s+|\b),(?:\s+|\b)",
    ]
    _title_suffix_remove = [" single version", " (single version)", " radio edit"]
    _punctuation_remove = ["'", "’", "?", "#", "*", "!"]
    _punctuation_replace = ["/", "-", "."]

    _re_whitespaces = re.compile(r"\s+")
    _re_slug1 = re.compile(r"[^-\w\s_]")
    _re_slug2 = re.compile(r"[-_\s]+")
    _spellings = [
        {"check": "cryin", "re": re.compile(r"\bcryin\b"), "repl": "crying"},
        {"check": "%", "re": re.compile(r"%"), "repl": " percent "},
    ]
    _re_built = {}

    @classmethod
    def _re_punctuation_replace(cls):
        return cls._re_builder("_re_punctuation_replace", (cls._punctuation_replace,))

    @classmethod
    def _re_title_artist_1(cls):
        return cls._re_builder(
            "_re_title_artist_1", (cls._title_artist_1, False, False)
        )

    @classmethod
    def _re_title_artist_2(cls):
        return cls._re_builder(
            "_re_title_artist_2", (cls._title_artist_2, False, False)
        )

    @classmethod
    def _re_punctuation_remove(cls):
        return cls._re_builder("_re_punctuation_remove", (cls._punctuation_remove,))

    @classmethod
    def _re_split_artists(cls):
        return cls._re_builder(
            "_re_split_artists",
            (cls._artist_delimiters, False, False),
        )

    @classmethod
    def _build_re_list(
        cls, values: list[str], escape: bool = True, allow_multiple: bool = True
    ):
        items = [
            f"{re.escape(i) if escape else i}{'+' if allow_multiple else ''}"
            for i in values
        ]
        joined = "|".join(items)
        return re.compile(rf"(?:{joined})")

    @classmethod
    def _re_builder(cls, key, value):
        found = cls._re_built.get(key)
        if found is None:
            cls._re_built[key] = cls._build_re_list(*value)
            found = cls._re_built.get(key)
        else:
            pass
        return found

    def queries(self, track: Track):
        """Build a query for a service from a normalise track."""
        self.normalise_track(track)
        result = track.normalised.queries
        return result

    def most_played(self, track_list: TrackList) -> TrackList:
        """Convert a list of tracks into an ordered list from the most to least played."""
        groups = {}
        for track in track_list.tracks:
            key = "-".join([i for i in track.artists + [track.title] if i])
            if key not in groups:
                groups[key] = []
            groups[key].append(track)

        raw = sorted(
            [(k, len(v), v) for k, v in groups.items() if len(v) > 1],
            key=lambda x: x[1],
            reverse=True,
        )
        return TrackList(
            title=track_list.title,
            type=TrackListType.ORDERED,
            tracks=[ts[0] for k, c, ts in raw],
        )

    def normalise_tracklist(self, item: TrackList) -> None:
        """Normalise each track in a list."""
        for track in item.tracks:
            self.normalise_track(track)

    def normalise_track(self, item: Track) -> None:
        """Normalise a track."""
        if item is None:
            return
        if item.normalised is not None:
            return
        normalised = self.normalise_info(item.title, item.artists)
        item.set_normalised(normalised)

    def normalise_info(
        self, title: str | None, artists: list[str] | None
    ) -> TrackNormalised:
        """Normalise a title and artists."""
        title_norm = str(title if title is not None else "")
        artists_norm = [str(i) for i in (artists if artists is not None else [])]
        steps = []

        title_norm, artists_norm = self._normalise_step(
            steps,
            "collapse_spaces1",
            self._normalise_collapse_spaces(title_norm),
            [self._normalise_collapse_spaces(i) for i in artists_norm],
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "case",
            self._normalise_case(title_norm),
            [self._normalise_case(i) for i in artists_norm],
        )
        title_split, title_artists = self._normalise_split_title_artist(title_norm)
        title_norm, artists_norm = self._normalise_step(
            steps,
            "split_artist",
            title_split,
            [
                *[a for i in artists_norm for a in self._normalise_split_artist(i)],
                *title_artists,
            ],
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "punctuation",
            self._normalise_punctuation(title_norm),
            [self._normalise_punctuation(i) for i in artists_norm],
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "constants",
            self._normalise_constants(title_norm),
            artists_norm,
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "spelling",
            self._normalise_spelling(title_norm),
            [self._normalise_spelling(i) for i in artists_norm],
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "encoding",
            self._normalise_encoding(title_norm),
            [self._normalise_encoding(i) for i in artists_norm],
        )
        title_norm, artists_norm = self._normalise_step(
            steps,
            "collapse_spaces2",
            self._normalise_collapse_spaces(title_norm),
            [self._normalise_collapse_spaces(i) for i in artists_norm],
        )

        result = TrackNormalised(title=title_norm, artists=artists_norm)
        return result

    def _normalise_step(
        self,
        steps: list[dict[str, typing.Any]],
        name: str,
        title: str,
        artists: list[str],
    ) -> tuple[str, list[str]]:
        step = {"name": name, "title": title, "artists": artists}
        steps.append(step)

        if len(steps) > 1 and name != "case":
            cur = (step["title"], step["artists"])
            prev = (steps[-2]["title"], steps[-2]["artists"])
            if step["title"] != steps[-2]["title"]:
                pass
            if step["artists"] != steps[-2]["artists"]:
                pass

        return step["title"], step["artists"]

    @functools.cache
    def _normalise_collapse_spaces(self, value: str) -> str:
        return self._re_whitespaces.sub(" ", value).strip()

    @functools.cache
    def _normalise_remove_spaces(self, value: str) -> str:
        return self._re_whitespaces.sub("", value)

    @functools.cache
    def _normalise_split_title_artist(self, value: str) -> tuple[str, list[str]]:
        """Split the title to extract artist names."""
        # two phases:
        # first phase splits on a different set of delimiters to keep the title intact
        # second phase is normalise_split_artist
        phase1 = []
        for i in self._re_title_artist_1().split(value):
            i = i.strip()
            if i:
                phase1.append(i)

        if len(phase1) > 1:
            result = []
            for i in phase1[1:]:
                for a in self._re_title_artist_2().split(i):
                    a = a.strip()
                    if a:
                        result.append(a)
            return phase1[0], result
        return phase1[0] if len(phase1) > 0 else "", []

    @functools.cache
    def _normalise_split_artist(self, value: str) -> list[str]:
        """Split artist names into separate items."""
        result = []
        for a in self._re_split_artists().split(value):
            a = a.strip()
            if a:
                result.append(a)
        return result

    @functools.cache
    def _normalise_case(self, value: str) -> str:
        return value.casefold()

    @functools.cache
    def _normalise_punctuation(self, value: str) -> str:
        first = self._re_punctuation_remove().sub("", value)
        second = self._re_punctuation_replace().sub(" ", first).strip()
        return second

    @functools.cache
    def _normalise_constants(self, value: str) -> str:
        items = self._title_suffix_remove
        result = str(value)
        for item in items:
            if result.endswith(item):
                length = len(item)
                result = result[0:-length].strip()
                return result
        return result

    @functools.cache
    def _normalise_spelling(self, value: str) -> str:
        result = str(value)
        for spelling in self._spellings:
            check = spelling["check"]
            regex = spelling["re"]
            repl = spelling["repl"]
            if check in result:
                result = regex.sub(repl, value)
        return result

    @functools.cache
    def _normalise_encoding(self, value: str) -> str:
        """Normalise a string's encoding."""
        return (
            unicodedata.normalize("NFKD", str(value))
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    def match(
        self, track: Track, available: list[Track], first_count: int
    ) -> Track | None:
        self.normalise_track(track)

        track_title_norm = self._normalise_remove_spaces(track.normalised.title)
        track_artists_norm = [
            self._normalise_remove_spaces(i) for i in track.normalised.artists
        ]

        haystack = available[:first_count]
        for other in haystack:
            self.normalise_track(other)

            other_title_norm = self._normalise_remove_spaces(other.normalised.title)
            other_artists_norm = [
                self._normalise_remove_spaces(i) for i in other.normalised.artists
            ]

            matched_title = track_title_norm == other_title_norm

            a_in_b_artists = all(i in other_artists_norm for i in track_artists_norm)
            b_in_a_artists = all(i in track_artists_norm for i in other_artists_norm)
            matched_artists = a_in_b_artists or b_in_a_artists

            if matched_title and matched_artists:
                logger.debug(
                    "Matched track %s to query result %s ('%s' == '%s').",
                    track,
                    other,
                    track.normalised,
                    other.normalised,
                )
                return other
            logger.debug(
                "No match for track %s to query result %s ('%s' != '%s').",
                track,
                other,
                track.normalised,
                other.normalised,
            )

        logger.debug(
            "No match for track %s in first %s query results.", track, len(haystack)
        )

        return None
