from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase, Undefined, config


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Streamable:

    text: str = field(metadata=config(field_name="#text"))
    fulltrack: str
