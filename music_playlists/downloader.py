import json
import logging
from os import makedirs
from os.path import join, isfile
from typing import Optional, Dict, List, Any, Union

import requests
from boltons.strutils import slugify


class CacheEntry:
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value


class Downloader:
    """Downloads resources and stores in a named cache."""
    _logger = logging.getLogger(__name__)

    cache_temp = 'cache_temp'
    cache_persisted = 'cache_persist'

    def download_text(self, cache_name: str, url: str) -> Optional[str]:
        return self._download(cache_name, url, 'text')

    def download_json(self, cache_name: str, url: str) -> Optional[Union[Dict, List]]:
        return self._download(cache_name, url, 'json')

    def _download(self, cache_name: str, url: str, content_type: str):
        # load from cache
        if content_type == 'json':
            content = self.retrieve_object(cache_name, url)
        else:
            content = self.retrieve_page(cache_name, url)
        if content is not None:
            return content.get_value()

        # get from website
        self._logger.info(f"Downloading '{content_type}' to cache '{cache_name}' from '{url}'")
        page = requests.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        elif content_type == 'json':
            content = page.json()
        else:
            content = page.text

        # store content, even if it is empty or None
        if content_type == 'json':
            self.store_object(cache_name, url, content)
        else:
            self.store_page(cache_name, url, content)

        if not content:
            return None

        return content

    def cache_item_id(self, key) -> str:
        if not key:
            raise Exception('Must provide a cache key.')
        item_id = slugify(key, delim='_', ascii=True).decode('utf-8').strip().casefold()
        return item_id

    def store_page(self, cache_name: str, url: str, content: Any) -> bool:
        return self._cache_save(cache_name, url, content)

    def retrieve_page(self, cache_name: str, url: str) -> Optional[CacheEntry]:
        return self._cache_load(cache_name, url)

    def store_object(self, cache_name: str, key: str, value: Any) -> bool:
        return self._cache_save(cache_name, key, json.dumps(value), ext='json')

    def retrieve_object(self, cache_name: str, key: str) -> Optional[CacheEntry]:
        value = self._cache_load(cache_name, key, ext='json')
        if isinstance(value, CacheEntry):
            return CacheEntry(json.loads(value.get_value()))
        return None

    def _cache_save(self, cache_name: str, key: str, value: Any, ext: str = 'txt') -> bool:
        makedirs(cache_name, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(cache_name, item_id + '.' + ext)

        self._logger.debug(f"Saving cache '{cache_name}' for '{key}' to '{file_path}'")

        with open(file_path, 'wb') as f:
            f.write(value.encode('utf-8'))
        return True

    def _cache_load(self, cache_name: str, key: str, ext: str = 'txt') -> Optional[CacheEntry]:
        makedirs(cache_name, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(cache_name, item_id + '.' + ext)

        if not isfile(file_path):
            self._logger.info(f"Cache '{cache_name}' does not contain '{key}' from '{file_path}'")
            return None

        self._logger.debug(f"Loading cache '{cache_name}' for '{key}' from '{file_path}'")

        with open(file_path, 'rb') as f:
            return CacheEntry(f.read().decode('utf-8'))
