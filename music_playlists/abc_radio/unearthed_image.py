from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase, Undefined, config


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class UnearthedImage:
    """Unearthed Image."""

    url: str
