from typing import Optional, List

from music_playlists.track import Track


class SourcePlaylist:
    """Retrieves tracks in a source playlist."""

    code = None
    title = None

    def get_playlist_tracks(self, limit: Optional[int] = None) -> List[Track]:
        """Get the tracks in the source playlist."""
        raise NotImplementedError()
