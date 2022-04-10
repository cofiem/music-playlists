from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, Undefined, config

from music_playlists.youtube_music.album import Album
from music_playlists.youtube_music.artist import Artist
from music_playlists.youtube_music.feedback import Feedback
from music_playlists.youtube_music.thumbnail import Thumbnail


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Track:
    title: str
    artists: list[Artist]
    thumbnails: list[Thumbnail]
    is_explicit: bool = field(metadata=config(field_name="isExplicit"))
    duration: Optional[str] = None
    duration_seconds: Optional[int] = None
    video_id: Optional[str] = field(metadata=config(field_name="videoId"), default=None)
    views: Optional[str] = None
    album: Optional[Album] = None
    feedback_tokens: Optional[Feedback] = field(
        metadata=config(field_name="feedbackTokens"), default=None
    )
    is_available: Optional[bool] = field(
        metadata=config(field_name="isAvailable"), default=None
    )
    like_status: Optional[str] = field(
        metadata=config(field_name="likeStatus"), default=None
    )
    set_video_id: Optional[str] = field(
        metadata=config(field_name="setVideoId"), default=None
    )
    year: Optional[str] = None
    category: Optional[str] = None
    result_type: Optional[str] = field(
        metadata=config(field_name="resultType"), default=None
    )
