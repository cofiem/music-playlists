import functools
import logging

from datetime import timedelta
from pathlib import Path

import cattr

from beartype import beartype
from requests import Session
from requests_cache import CachedSession, SQLiteCache


c = cattr.GenConverter(forbid_extra_keys=True)

logger = logging.getLogger(__name__)


@beartype
class Downloader:
    """Provides a shared downloader that can cache resources."""

    def __init__(
        self,
        store_path: Path = None,
        expire_days: float | None = None,
        timeout: int | None = 30,
    ):
        if store_path is None:
            self._session = Session()
            self._session.request = functools.partial(
                self._session.request, timeout=timeout
            )
            logger.info(
                "Created standard session that does not cache with time out %s.",
                timeout,
            )
        else:
            file_path = store_path / "http_cache.sqlite"
            backend = SQLiteCache(file_path, timeout=timeout)

            if expire_days is None:
                expire_after = None
            else:
                expire_after = timedelta(days=expire_days)

            self._session = CachedSession(
                backend=backend,
                timeout=timeout,
                expire_after=expire_after,
                allowable_methods=("GET", "POST"),
                allowable_codes=(200, 201),
            )
            logger.info(
                "Created cached session with timeout %s using sqlite expiring after %s at %s.",
                timeout,
                expire_after or "(never)",
                file_path,
            )

    @property
    def get_session(self):
        return self._session
