import json
import logging
from os import makedirs
from os.path import join, isfile
from typing import Optional, Dict, List, Any, TypeVar, Union

import requests
from boltons.strutils import slugify

StoredTypes = TypeVar('StoredTypes', Dict, List, str)


class CacheEntry:
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value


class Downloader:
    _logger = logging.getLogger(__name__)

    def __init__(self, use_cache=True):
        self._use_cache = use_cache
        self._local_cache_dir = 'cache'

    def download_text(self, url: str) -> Optional[str]:
        # load from cache
        content = self.cache_load_page(url)
        if content is not None:
            return content.get_value()

        # get from website
        self._logger.info(f"Downloading text from '{url}'")
        page = requests.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.text
            self.cache_save_page(url, content)

        if not content:
            return None

        return content

    def download_json(self, url: str) -> Optional[Union[Dict, List]]:
        # load from cache
        content = self.cache_load_object(url)
        if content is not None:
            return content.get_value()

        # get from website
        self._logger.info(f"Downloading json from '{url}'")
        page = requests.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.json()
            self.cache_save_object(url, content)

        if not content:
            return None

        return content

    def cache_item_id(self, url) -> str:
        if not url:
            raise Exception('Must provide a cache id.')
        item_id = slugify(url, delim='_', ascii=True).decode('utf-8').strip().casefold()
        return item_id

    def cache_save_page(self, url, content) -> bool:
        return self._cache_save(url, content)

    def cache_load_page(self, url) -> Optional[CacheEntry]:
        return self._cache_load(url)

    def cache_save_object(self, key: str, value: Any) -> bool:
        return self._cache_save(key, json.dumps(value), ext='json')

    def cache_load_object(self, key: str) -> Optional[CacheEntry]:
        value = self._cache_load(key, ext='json')
        if isinstance(value, CacheEntry):
            return CacheEntry(json.loads(value.get_value()))
        return None

    def _cache_save(self, key: str, value: Any, ext: str = 'txt') -> bool:
        if not self._use_cache:
            return False

        makedirs(self._local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(self._local_cache_dir, item_id + '.' + ext)

        self._logger.debug(f"Saving cache for '{key}' to '{file_path}'")

        with open(file_path, 'wb') as f:
            f.write(value.encode('utf-8'))
        return True

    def _cache_load(self, key: str, ext: str = 'txt') -> Optional[CacheEntry]:
        if not self._use_cache:
            return None

        makedirs(self._local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(self._local_cache_dir, item_id + '.' + ext)

        if not isfile(file_path):
            self._logger.warning(f"Cache does not contain '{key}' from '{file_path}'")
            return None

        self._logger.debug(f"Loading cache for '{key}' from '{file_path}'")

        with open(file_path, 'rb') as f:
            return CacheEntry(f.read().decode('utf-8'))
