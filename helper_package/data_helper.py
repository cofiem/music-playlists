import json
import logging
from os import makedirs
from os.path import abspath, join, dirname, isfile
import string
from typing import Optional, Dict, Tuple
import yaml

import requests


class DataHelper:
    allowed_chars = string.digits + string.ascii_letters + string.punctuation

    cache_chars = string.digits + string.ascii_letters
    local_cache_dir = 'cache'
    use_cache = True

    def __init__(self):
        self._logger = logging.getLogger('music_playlists.DataHelper')

    # ---------- Normalise Artist name and Track title --

    def normalise(self, title: str, artist: str) -> Tuple[str, str]:
        featuring = ''
        new_title = title.lower().strip()

        changes_file = abspath(join(dirname(abspath(__file__)), '..', 'data', 'changes.yml'))
        with(open(changes_file, 'rt')) as f:
            changes = yaml.safe_load(f)

        if 'title_replace' in changes:
            for find, replace in changes['title_replace'].items():
                new_title = new_title.replace(find.lower().strip(), replace.lower().strip())

        if 'title_featuring' in changes:
            for find, replace in changes['title_featuring'].items():
                if find in new_title:
                    artist_featuring = new_title[(new_title.index(find) + len(find)):]
                    featuring = f"{featuring}, {artist_featuring}".strip(', ')
                    new_title = new_title.replace(find, replace)

        new_title = new_title.strip()
        featuring = featuring.replace(artist.lower().strip(), '').strip(', ')

        return new_title, featuring

    # ---------- Downloading -----------------------------

    def download_text(self, url: str) -> Optional[str]:
        # load from cache
        content_raw = self.cache_load_page(url)
        if content_raw:
            return content_raw.decode('utf-8')

        # get from website
        page = requests.get(url)

        self._logger.debug(f'Downloading text from {url}')

        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.text
            self.cache_save_page(url, content.encode('utf-8'))

        if not content:
            return None

        return content

    def download_json(self, url: str) -> Optional[Dict]:
        # load from cache
        content_raw = self.cache_load_page(url)
        if content_raw:
            return json.loads(content_raw.decode('utf-8'))

        # get from website
        page = requests.get(url)

        self._logger.debug(f'Downloading json from {url}')

        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.json()
            self.cache_save_page(url, json.dumps(content).encode('utf-8'))

        if not content:
            return None

        return content

    # ---------- Local Cache -----------------------------

    def cache_item_id(self, url) -> str:
        item_id = ''.join(c if c in self.cache_chars else '' for c in url).strip()
        return item_id.lower()

    def cache_save_page(self, url, content) -> None:
        if not self.use_cache:
            return

        makedirs(self.local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(url)
        file_path = join(self.local_cache_dir, item_id + '.txt')

        self._logger.debug(f'Saving cache for {url}')

        with open(file_path, 'wb') as f:
            f.write(content)

    def cache_load_page(self, url) -> Optional[bytes]:
        if not self.use_cache:
            return None

        makedirs(self.local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(url)
        file_path = join(self.local_cache_dir, item_id + '.txt')

        if not isfile(file_path):
            return None

        self._logger.debug(f'Loading cache for {url}')

        with open(file_path, 'rb') as f:
            return f.read()
