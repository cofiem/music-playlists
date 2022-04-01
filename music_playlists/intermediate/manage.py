import logging
from itertools import groupby
from typing import Optional

from boltons.strutils import slugify

from music_playlists.intermediate.track import Track
from music_playlists.intermediate.track_list import TrackList


class Manage:

    code = "intermediate"

    _logger = logging.getLogger(code)

    def queries(self, track: Track):
        title = str(track.title)
        artists = list(track.artists)
        # spaces
        title = self._collapse_spaces(title)
        artists = [self._collapse_spaces(i) for i in artists]
        # case
        title = self._normalise_case(title)
        artists = [self._normalise_case(i) for i in artists]
        # split artists
        title, artists = self._split_artists(title, artists)
        # title constants
        title = self._known_title_constants(title)
        # punctuation
        title = self._normalise_punctuation(title)
        artists = [self._normalise_punctuation(i) for i in artists]
        # featured artists
        title, artists = self._featured_artists(title, artists)

        results = []
        artist_length = len(artists)
        for index in range(artist_length):
            stop = artist_length - index
            artists_sel = [a for a in artists[0:stop] if a]
            query = " ".join(artists_sel + [title]).strip()
            results.append(query)

        return results

    def match(self, track: Track, available: list[Track]) -> Optional[Track]:
        for other in available[:5]:
            # exact
            a_title = str(track.title)
            a_artists = list(track.artists)
            b_title = str(other.title)
            b_artists = list(other.artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # spaces
            a_title = self._collapse_spaces(a_title)
            a_artists = [self._collapse_spaces(i) for i in a_artists]
            b_title = self._collapse_spaces(b_title)
            b_artists = [self._collapse_spaces(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # case
            a_title = self._normalise_case(a_title)
            a_artists = [self._normalise_case(i) for i in a_artists]
            b_title = self._normalise_case(b_title)
            b_artists = [self._normalise_case(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # split artists
            a_title, a_artists = self._split_artists(a_title, a_artists)
            b_title, b_artists = self._split_artists(b_title, b_artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # title constants
            a_title = self._known_title_constants(a_title)
            b_title = self._known_title_constants(b_title)

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # punctuation
            a_title = self._normalise_punctuation(a_title)
            a_artists = [self._normalise_punctuation(i) for i in a_artists]
            b_title = self._normalise_punctuation(b_title)
            b_artists = [self._normalise_punctuation(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # featured artists
            a_title, a_artists = self._featured_artists(a_title, a_artists)
            b_title, b_artists = self._featured_artists(b_title, b_artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                return other

            # extra artists
            if self._compare_allow_extra_artists(
                a_title, a_artists, b_title, b_artists
            ):
                return other

            # for debugging
            # self._logger.info(
            #     f"Track '{a_title}' '{a_artists}' does not match '{b_title}' '{b_artists}'"
            # )

        # for debugging
        # count = len(available)
        # self._logger.info(f"No match in {count} for track {track}")

        return None

    def _compare(
        self, a_title: str, a_artists: list[str], b_title: str, b_artists: list[str]
    ):
        title = a_title == b_title
        artists = a_artists == b_artists
        return title and artists

    def _remove_chars(self, chars: str, value: str):
        result = value
        for char in chars:
            result = result.replace(char, "")
        return result

    def _collapse_spaces(self, value: str):
        result = ""
        previous = None
        for char in value or "":
            if previous == " " and char == " ":
                continue
            result += char

        return result.strip()

    def _normalise_case(self, value: str):
        return (value or "").casefold()

    def _split_artists(self, title: str, artists: list[str]):
        seps = [" x ", " & ", " + ", ", ", " and "]
        result = []
        for artist in artists:
            for sep in seps:
                for i in artist.split(sep):
                    if i not in result and all(s not in i for s in seps):
                        result.append(i)
        return title, result

    def _featured_artists(self, title: str, artists: list[str]):
        sep = ", "

        prefixes = ["feat.", "with", "ft."]
        for prefix in prefixes:
            start = f"({prefix} "
            if start not in title or not title.endswith(")"):
                continue

            find_index = title.index(start)
            artist_index = find_index + len(start)

            artists_str = title[artist_index:-1].replace(" & ", sep)
            artists_split = artists_str.split(sep)

            r_title = title[0:find_index].strip()
            r_artists = list(artists)

            for a in artists_split:
                a = a.strip()
                if a not in r_artists:
                    r_artists.append(a)
            return r_title, r_artists

        return title, artists

    def _normalise_punctuation(self, value: str):
        chars = r"'’?#/*-"
        result = self._remove_chars(chars, value)
        return result

    def _compare_allow_extra_artists(
        self, a_title: str, a_artists: list[str], b_title: str, b_artists: list[str]
    ):
        title = a_title == b_title
        if not title:
            return False

        a_in_b_artists = all(i in b_artists for i in a_artists)
        b_in_a_artists = all(i in a_artists for i in b_artists)
        artists = a_in_b_artists or b_in_a_artists
        return artists

    def _known_title_constants(self, title: str):
        items = [" - single version", " (single version)"]
        for item in items:
            if title.endswith(item):
                length = len(item)
                result = title[0:-length].strip()
                return result
        return title

    def most_played(self, track_list: TrackList) -> TrackList:
        groups = {}
        for track in track_list.tracks:
            key = "-".join(track.artists + [track.title])
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
            type=TrackList.type_ordered(),
            tracks=[ts[0] for k, c, ts in raw],
        )
