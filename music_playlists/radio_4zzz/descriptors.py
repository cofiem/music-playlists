from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Descriptors:
    """4zzz playlist track descriptors"""

    is_australian: bool
    is_local: bool
    is_female: bool
    is_indigenous: bool
    is_new: bool
    is_gender_non_conforming: Optional[bool]
