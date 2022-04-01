from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Program:
    """4zzz program"""

    url: Optional[str]
    guide_url_override: Optional[str]
    name: str
    broadcasters: str
    description: Optional[str]
    grid_description: Optional[str]
    twitter_handle: Optional[str]
    podcast_url: Optional[str]
    podcast_url2: Optional[str]
    default_first_aired_guide: str
    slug: str
    banner_image_url: Optional[str]
    banner_image_small: Optional[str]
    profile_image_url: Optional[str]
    profile_image_small: Optional[str]
    facebook_page: Optional[str]
    episodes_rest_url: str
