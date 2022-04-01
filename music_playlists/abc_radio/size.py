from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Size:
    url: str
    width: int
    height: int
    aspect_ratio: str
