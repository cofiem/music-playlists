import logging
from dataclasses import dataclass, field
from typing import List, Any, Dict

from boltons.strutils import slugify


@dataclass
class Track:
    """Details for a generic track."""
    name: str
    artists: List[str]

    name_normalised: str = field(default=None)
    artist: str = field(default=None)
    featured: List[str] = field(default_factory=list)

    query_strings: List[str] = field(default_factory=list)

    info: Dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def __str__(self) -> str:
        return f"{self.name} - {', '.join(self.artists)}"

    def __post_init__(self):
        """Populate any empty optional fields."""
        self._logger = logging.getLogger(__name__)
        self._populate()

    def is_match(self, match: 'Track') -> bool:
        query_title = slugify(self.name_normalised)
        query_artist = slugify(self.artist)
        query_featured = slugify(', '.join(self.featured))
        result_title = slugify(match.name_normalised)
        result_artist = slugify(match.artist)
        result_featured = slugify(', '.join(match.featured))

        match_title = query_title in result_title
        # match_artist = query_artist in result_artist
        match_featuring = query_featured in result_featured
        match_featuring2 = result_featured in query_featured

        equal_title = query_title == result_title
        equal_artist = query_artist == result_artist
        # equal_featuring = query_featured == result_featured

        has_featuring = query_featured and result_featured

        # these are the variations that are valid
        if equal_title and equal_artist and match_featuring and has_featuring:
            return True
        if match_title and equal_artist and match_featuring and not has_featuring:
            return True
        if equal_title and equal_artist and has_featuring and (match_featuring or match_featuring2):
            return True

        return False

    def _populate(self):
        # baseline
        track = self.name.lower() if self.name else ''
        artist = self.artists[0].lower() if len(self.artists) > 0 else ''
        featured = ([i.lower() for i in self.artists[1:]] if len(self.artists) > 1 else [])  # type: List[str]

        # replace chars
        replace_chars = {"’": "'"}
        for k, v in replace_chars.items():
            track = track.replace(k, v)
            artist = artist.replace(k, v)
            featured = [i.replace(k, v) for i in featured]

        # extract artists
        track_featured = self._extract_artists(track, featured)
        track = track_featured[0]
        featured = track_featured[1:]

        artist_featured = self._extract_artists(artist, featured)
        artist = artist_featured[0]
        featured = artist_featured[1:]

        # remove chars
        remove_chars = '[](){},-#=&_'
        for item in remove_chars:
            track = track.replace(item, ' ')
            artist = artist.replace(item, ' ')
            featured = [i.replace(item, ' ') for i in featured]

        # final clean up
        track = track.strip()
        artist = artist.strip()
        featured = [i.replace(track, ' ').replace(artist, ' ').strip(', ') for i in featured if i]

        # replacements for known misspellings
        replacements = [
            {'match_artist': 'thelma plum', 'match_track': 'better in black',
             'replace_artist': 'thelma plum', 'replace_track': 'better in blak'},
            {'match_artist': 'zac eichner', 'match_track': 'lucy   live at jive',
             'replace_artist': 'zac eichner', 'replace_track': 'lucy'},
        ]
        for replacement in replacements:
            if replacement['match_track'] == track and \
                    replacement['match_artist'] == artist:
                track = replacement['replace_track']
                artist = replacement['replace_artist']

        # set empty fields
        if not self.name_normalised and track:
            self.name_normalised = track
        if not self.artist and artist:
            self.artist = artist
        if not self.featured and featured:
            self.featured = featured

        # set query strings
        query1 = f"{self.name_normalised} - {self.artist} {', '.join(self.featured)}".strip()
        query2 = f"{self.name_normalised} - {self.artist}".strip()
        queries = [query1]
        if query2 != query1:
            queries.append(query2)
        self.query_strings = queries

    def _extract_artists(self, first: str, remaining: List[str]) -> List[str]:
        seps = ['[', ']', '{', '}', ' ft ', ' ft. ', ' feat ', ' feat. ', ' featuring ', ' w/ ', ' x ', ',']
        placeholder1 = ' ->|sep|<- '
        placeholder2 = '->|sep|<-'
        source = first + placeholder1 + placeholder1.join(remaining or [])
        source = source.replace('(', ' ').replace(')', ' ')

        for sep in seps:
            source = source.replace(sep, placeholder1)

        results = source.split(placeholder2)

        # the first item is the first, the rest is the remaining
        norm_first = (results[0] if results else '').strip()
        norm_remaining = list(
            set(i.strip() for i in results[1:] if i and i.strip() and norm_first.strip() != i.strip()))

        if any(placeholder2 in i for i in norm_remaining):
            raise Exception(f"Text should not contain placeholder ({placeholder2}): '{norm_remaining}'")

        result = [norm_first] + norm_remaining

        for sep in seps:
            for text in result:
                if sep in text:
                    raise Exception(f"Found a separator '{sep}' in result '{text}'")

        return result
