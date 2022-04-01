from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class EpisodeSummary:
    """4zzz episode summary"""

    url: Optional[str]
    start: str
    end: str
    duration: int
    multiple_eps_on_day: bool
    title: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    small_image_url: Optional[str]
    episode_rest_url: str
    current_episode: Optional[bool] = False
