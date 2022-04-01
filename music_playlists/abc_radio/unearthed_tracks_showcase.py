from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase, Undefined

from music_playlists.abc_radio.unearthed_track import UnearthedTrack


@dataclass_json(undefined=Undefined.RAISE, letter_case=LetterCase.CAMEL)
@dataclass
class UnearthedTracksShowcase:
    track_of_the_day: UnearthedTrack
    popular_tracks: list[UnearthedTrack]
    discover_tracks: list[UnearthedTrack]
