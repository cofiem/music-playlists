from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Episode:
    """4zzz program episode"""

    notes: Optional[str]
    start: str
    end: str
    duration: int
    url: Optional[str]
    title: Optional[str]
    image_url: Optional[str]
    small_image_url: Optional[str]
    playlist_rest_url: str
