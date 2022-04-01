from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase, Undefined, config


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class UnearthedSourceFile:
    """Unearthed SourceFile."""

    file_name: str
    url: str
    duration_ms: int
