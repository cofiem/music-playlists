from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase, Undefined, config


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Testing:
    """4zzz playlist track testing"""

    date: str
    timezone_type: int = field(metadata=config(field_name="timezone_type"))
    timezone: str
