import logging

from beartype import beartype

from music_playlists.intermediate.models import TrackList, Track

logger = logging.getLogger("intermediate")


@beartype
class Manage:
    code = "intermediate"

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
        # different spellings
        title = self._different_spellings(title)
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

    def match(self, track: Track, available: list[Track]) -> Track | None:
        for other in available[:5]:
            # exact
            a_title = str(track.title)
            a_artists = list(track.artists)
            b_title = str(other.title)
            b_artists = list(other.artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "exact", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # spaces
            a_title = self._collapse_spaces(a_title)
            a_artists = [self._collapse_spaces(i) for i in a_artists]
            b_title = self._collapse_spaces(b_title)
            b_artists = [self._collapse_spaces(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "spaces", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # case
            a_title = self._normalise_case(a_title)
            a_artists = [self._normalise_case(i) for i in a_artists]
            b_title = self._normalise_case(b_title)
            b_artists = [self._normalise_case(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "case", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # split artists
            a_title, a_artists = self._split_artists(a_title, a_artists)
            b_title, b_artists = self._split_artists(b_title, b_artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "split artists",
                    a_title,
                    a_artists,
                    b_title,
                    b_artists,
                    track,
                    other,
                )
                return other

            # title constants
            a_title = self._known_title_constants(a_title)
            b_title = self._known_title_constants(b_title)

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "constants", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # different spellings
            a_title = self._different_spellings(a_title)
            b_title = self._different_spellings(b_title)

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "spelling", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # punctuation
            a_title = self._normalise_punctuation(a_title)
            a_artists = [self._normalise_punctuation(i) for i in a_artists]
            b_title = self._normalise_punctuation(b_title)
            b_artists = [self._normalise_punctuation(i) for i in b_artists]

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "puncuation", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # featured artists
            a_title, a_artists = self._featured_artists(a_title, a_artists)
            b_title, b_artists = self._featured_artists(b_title, b_artists)

            if self._compare(a_title, a_artists, b_title, b_artists):
                self._match_log(
                    "featured", a_title, a_artists, b_title, b_artists, track, other
                )
                return other

            # extra artists
            if self._compare_allow_extra_artists(
                a_title, a_artists, b_title, b_artists
            ):
                self._match_log(
                    "extra artists",
                    a_title,
                    a_artists,
                    b_title,
                    b_artists,
                    track,
                    other,
                )
                return other

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "No match for track '%s' '%s' in '%s' '%s'",
                    a_title,
                    a_artists,
                    b_title,
                    b_artists,
                )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("No match in %s for track %s", len(available), track)

        return None

    def _compare(
        self, a_title: str, a_artists: list[str], b_title: str, b_artists: list[str]
    ):
        title = a_title == b_title
        artists = sorted(a_artists) == sorted(b_artists)
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

        prefixes = ["feat.", "with", "ft.", "featuring"]
        delimiters = [("(", ")"), ("{", "}"), ("[", "]"), ('', '')]
        for prefix in prefixes:
            for delim_start, delim_end in delimiters:
                start = f"{delim_start}{prefix} "
                if start not in title or not title.endswith(delim_end):
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
        chars = r"'’?#/*-!"
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
            type=TrackList.type_ordered(),
            tracks=[ts[0] for k, c, ts in raw],
        )

    def _different_spellings(self, title: str):
        spellings = {
            "crying": ["cryin"],
        }
        title_split = title.split(" ")
        for replacement, alternates in spellings.items():
            for alternate in alternates:
                for index, word in enumerate(title_split):
                    if alternate == word:
                        title_split[index] = replacement
        return " ".join(title_split)

    def _match_log(
        self, name, a_title, a_artists, b_title, b_artists, track: Track, other: Track
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Match for track '%s' '%s' in '%s' '%s' after '%s' (original track '%s' '%s'; other '%s' '%s')",
                a_title,
                a_artists,
                b_title,
                b_artists,
                name,
                track.title,
                track.artists,
                other.title,
                other.artists,
            )
