from dataclasses import dataclass
from typing import List, Any, Dict


@dataclass
class Track:
    """A track that may be part of a playlist."""

    origin_code: str
    track_id: str
    title: str
    artists: List[str]
    query_strings: List[str]
    info: Dict[str, Any]

    def __str__(self) -> str:
        return f"{self.title} - {', '.join(self.artists)}"

    @classmethod
    def create(
        cls,
        code: str,
        track_id: str,
        original_title: str,
        original_artists: list[str],
        info,
    ):
        # baseline
        track_title = original_title.lower() if original_title else ""
        artist = original_artists[0].lower() if len(original_artists) > 0 else ""
        featured = (
            [i.lower() for i in original_artists[1:]]
            if len(original_artists) > 1
            else []
        )

        # replace chars
        replace_chars = {"’": "'"}
        for k, v in replace_chars.items():
            track_title = track_title.replace(k, v)
            artist = artist.replace(k, v)
            featured = [i.replace(k, v) for i in featured]

        # extract artists
        track_featured = cls._extract_artists(track_title, featured)
        track_title = track_featured[0]
        featured = track_featured[1:]

        artist_featured = cls._extract_artists(artist, featured)
        artist = artist_featured[0]
        featured = artist_featured[1:]

        # remove chars
        remove_chars = "[](){},-#=&_"
        for item in remove_chars:
            track_title = track_title.replace(item, " ")
            artist = artist.replace(item, " ")
            featured = [i.replace(item, " ") for i in featured]

        # final clean up
        track_title = track_title.strip()
        artist = artist.strip()
        featured = [
            i.replace(track_title, " ").replace(artist, " ").strip(", ")
            for i in featured
            if i
        ]

        # build query strings
        query1 = f"{track_title} - {artist} {', '.join(featured)}".strip()
        query2 = f"{track_title} - {artist}".strip()
        queries = [query1]
        if query2 != query1:
            queries.append(query2)

        return Track(
            origin_code=code,
            track_id=track_id,
            title=track_title,
            artists=[artist] + featured,
            query_strings=queries,
            info=info,
        )

    @classmethod
    def _extract_artists(cls, first: str, remaining: List[str]) -> List[str]:
        seps = [
            "[",
            "]",
            "{",
            "}",
            " ft ",
            " ft. ",
            " feat ",
            " feat. ",
            " featuring ",
            " w/ ",
            " x ",
            ",",
            " live at ",
        ]
        placeholder1 = " ->|sep|<- "
        placeholder2 = "->|sep|<-"
        source = first + placeholder1 + placeholder1.join(remaining or [])
        source = source.replace("(", " ").replace(")", " ")

        for sep in seps:
            source = source.replace(sep, placeholder1)

        results = source.split(placeholder2)

        # the first item is the first, the rest is the remaining
        norm_first = (results[0] if results else "").strip()
        norm_remaining = list(
            set(
                i.strip()
                for i in results[1:]
                if i and i.strip() and norm_first.strip() != i.strip()
            )
        )

        if any(placeholder2 in i for i in norm_remaining):
            raise Exception(
                f"Text should not contain placeholder ({placeholder2}): '{norm_remaining}'"
            )

        result = [norm_first] + norm_remaining

        for sep in seps:
            for text in result:
                if sep in text:
                    raise Exception(f"Found a separator '{sep}' in result '{text}'")

        return result
