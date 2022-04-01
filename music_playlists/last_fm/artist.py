from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase, Undefined


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class Artist:

    name: str
    mbid: str
    url: str
