from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Link:
    entity: str
    arid: str
    url: str
    id_component: Optional[str]
    title: str
    mini_synopsis: Optional[str]
    short_synopsis: Optional[str]
    medium_synopsis: Optional[str]
    type: str
    provider: str
    external: bool
    service_id: Optional[str] = None
