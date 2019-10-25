import json
import logging
from os import makedirs
from os.path import abspath, join, dirname, isfile
import string
from typing import Optional, Dict, Tuple, List, Any
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
        self._logger.info(f'Downloading text from {url}')
        page = requests.get(url)
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
        self._logger.info(f'Downloading json from {url}')
        page = requests.get(url)
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

        self._logger.info(f'Saving cache for {url}')

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

        self._logger.info(f'Loading cache for {url}')

        with open(file_path, 'rb') as f:
            return f.read()

    # ---------- Select song and build playlist data  -----------------------------

    def select_song(self, song_hits: List[Dict], query_title: str, query_artist: str):
        count = len(song_hits)
        self._logger.debug(f'Selecting song from {count} options')

        # if there are songs, then no match
        if count == 0:
            self._logger.warning(f'Did not select a song for "{query_title} - {query_artist}"')
            return {}

        # if there are results, then the query title and artist must appear in the result
        for song in song_hits:
            if self._is_match(query_title, query_artist, song['track']['title'], song['track']['artist']):
                self._logger.info(f'Selected song "{song["track"]["title"]} - {song["track"]["artist"]}"')
                return song['track']

        # if there are no matches, then no match
        self._logger.warning(f'Did not select a song for "{query_title} - {query_artist}"')
        return {}

    def build_result(self, selected_song: Optional[Dict], query_song: Dict):
        selected_title = selected_song.get('title')
        selected_artist = selected_song.get('artist')

        return {
            'track_id': selected_song.get('storeId') or selected_song.get('trackId') or
                        selected_song.get('id') or selected_song.get('nid'),
            'title': selected_song.get('title'),
            'artist': selected_song.get('artist'),
            'match': self._is_match(query_song['title_compare'], query_song['artist'], selected_title, selected_artist)
        }

    def build_playlist(self, songs_found: Dict[str, Any], songs_missing: Dict[str, Any]) -> Dict[str, Any]:
        found_count = len(songs_found)
        missing_count = len(songs_missing)

        descr_prefix = f'Playlist includes {found_count} found songs, ' \
                       f'with {missing_count} missing songs. These songs are missing: '
        descr_missing = ', '.join([f'({index}) "{song["title"]} - {song["artist"]}"'
                                   for index, song in songs_missing.items()])
        description = f'{descr_prefix} {descr_missing}.'

        gmusic_song_ids = [None] * (len(songs_missing) + len(songs_found))
        for index, song in songs_found.items():
            gmusic_song_ids[int(index)] = song['gmusic']['track_id']

        return {
            'description': description,
            'gmusic_song_ids': [i for i in gmusic_song_ids if i],
        }

    def _is_match(self, query_title: str, query_artist: str, result_title: str, result_artist: str):
        if not query_title or not result_title or not query_artist or not result_artist:
            return False

        q_title = self.normalise(query_title, query_artist)
        q_artist = query_artist.lower().strip()
        r_title = self.normalise(result_title, result_artist)
        r_artist = result_artist.lower().strip()

        if q_title in r_title and q_artist == r_artist:
            return True

        if q_artist in r_artist and q_title == r_title:
            return True

        return False
