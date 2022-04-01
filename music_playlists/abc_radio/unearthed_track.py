from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined, config

from music_playlists.abc_radio.unearthed_artist import UnearthedArtist
from music_playlists.abc_radio.unearthed_image import UnearthedImage
from music_playlists.abc_radio.unearthed_source_file import UnearthedSourceFile


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class UnearthedTrack:
    """Unearthed Track."""

    id: str
    title: str
    codename: str
    explicit: bool
    uploaded_on: str
    played_on: list[str]
    genres: list[str]
    web_source_file: UnearthedSourceFile
    artist: UnearthedArtist
    image: Optional[UnearthedImage]
    # typename: str = field(metadata=config(field_name="__typename"))
