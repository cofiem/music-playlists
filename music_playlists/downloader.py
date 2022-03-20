import logging
from datetime import timedelta
from pathlib import Path
from typing import Optional, Dict, List, Union

from requests_cache import CachedSession, SQLiteCache


class CacheEntry:
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value


class Downloader:
    """Downloads resources and stores in a named cache."""

    cache_temp = "cache_temp"
    cache_persisted = "cache_persist"

    def __init__(self, logger: logging.Logger, store_path: Path = None):
        self._logger = logger
        timeout = 30
        if store_path:
            backend = SQLiteCache(store_path, timeout=timeout)
        else:
            backend = SQLiteCache("http_cache", use_memory=True, timeout=timeout)

        expire_after = timedelta(hours=2)
        self._session = CachedSession(
            backend=backend, timeout=timeout, expire_after=expire_after
        )

    @property
    def get_session(self):
        return self._session

    def download_text(self, url: str) -> Optional[str]:
        return self._download(url, "text")

    def download_json(self, url: str) -> Optional[Union[Dict, List]]:
        return self._download(url, "json")

    def _download(self, url: str, content_type: str):
        # get from website
        self._logger.debug(f"Downloading '{content_type}' from '{url}'")

        page = self._session.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        elif content_type == "json":
            content = page.json()
        else:
            content = page.text

        if not content:
            return None

        return content
