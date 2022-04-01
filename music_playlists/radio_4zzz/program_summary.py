from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class ProgramSummary:
    """4zzz program summary"""

    slug: Optional[str]
    name: str
    broadcasters: str
    grid_description: Optional[str]
    archived: bool
    program_rest_url: str
