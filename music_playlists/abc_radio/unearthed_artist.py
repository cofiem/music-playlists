from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined, config

from music_playlists.abc_radio.unearthed_image import UnearthedImage


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class UnearthedArtist:
    """UnearthedArtist"""

    profile_name: str
    slug: str
    image: Optional[UnearthedImage]
