from abc import abstractmethod

from beartype import beartype, typing

from music_playlists import intermediate as inter


@beartype
class Source(typing.Protocol):
    """A protocol for classes that obtain playlist data from a source."""

    code: str

    @classmethod
    @abstractmethod
    def available(
        cls,
    ) -> dict[str, typing.Callable[[typing.Self, str], inter.TrackList]]:
        raise NotImplementedError


@beartype
class ServiceClient(typing.Protocol):
    """A protocol for classes that act as a client to a remote service."""

    @abstractmethod
    def login(self) -> None:
        raise NotImplementedError


@beartype
class Service(typing.Protocol):
    """A protocol for classes that host streaming music playlists."""

    @property
    @abstractmethod
    def client(self) -> ServiceClient:
        raise NotImplementedError

    @abstractmethod
    def playlist_tracks(
        self, playlist_id: str, limit: int | None = 100, *args, **kwargs
    ) -> inter.TrackList:
        raise NotImplementedError

    @abstractmethod
    def search_tracks(
        self, query: str, limit: int | None = 5, *args, **kwargs
    ) -> inter.TrackList:
        raise NotImplementedError

    @abstractmethod
    def update_playlist_tracks(self, info: inter.ServicePlaylistTracks) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_playlist_details(self, info: inter.ServicePlaylistInfo) -> bool:
        raise NotImplementedError
