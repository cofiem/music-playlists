from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Track:
    title: str
    artists: list[str]
    origin_code: str
    raw: object

    title_normalised: Optional[str] = None
    artists_normalised: list[str] = field(default_factory=list)

    def __str__(self):
        c = self.origin_code
        t = self.title
        a = "', '".join(a for a in self.artists)
        return f"{c}: '{t}' - '{a}'"
