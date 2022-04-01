from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class ExternalId:
    isrc: Optional[str] = None
    """International Standard Recording Code"""

    ean: Optional[str] = None
    """"International Article Number"""

    upc: Optional[str] = None
    """Universal Product Code"""
