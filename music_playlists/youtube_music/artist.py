from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Artist:
    name: str
    id: Optional[str] = None
    type: Optional[str] = None
