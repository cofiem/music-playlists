from datetime import timedelta
from pathlib import Path

from beartype import beartype
from requests import Session
from requests_cache import CachedSession, SQLiteCache


@beartype
class Downloader:
    """Provides a shared downloader that caches resources."""

    def __init__(self, store_path: Path = None):
        timeout = 30
        if store_path:
            backend = SQLiteCache(store_path / 'http_cache.sqlite', timeout=timeout)
        else:
            backend = SQLiteCache("http_cache", use_memory=True, timeout=timeout)

        expire_after = timedelta(days=1.5)
        self._session = CachedSession(
            backend=backend,
            timeout=timeout,
            expire_after=expire_after,
            allowable_methods=("GET", "POST"),
            allowable_codes=(200, 201),
        )
        self._session_no_cache = Session()

    @property
    def get_session(self):
        return self._session

    @property
    def get_session_no_cache(self):
        return self._session_no_cache
