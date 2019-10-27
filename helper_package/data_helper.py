import json
import logging
import re
import unicodedata
from os import makedirs
from os.path import abspath, join, dirname, isfile
from typing import Optional, Dict, Tuple, List, Any, TypeVar

import requests

StoredTypes = TypeVar('StoredTypes', Dict, List, str)


class DataHelper:

    def __init__(self, use_cache=True):
        self._use_cache = use_cache
        self._logger = logging.getLogger('music_playlists.DataHelper')
        self._local_cache_dir = 'cache'
        self._cache_chars = '0123456789_-abcdefghijklmnopqrstruvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

        changes_file = abspath(join(dirname(abspath(__file__)), '..', 'data', 'remove.txt'))
        with(open(changes_file, 'rt')) as f:
            self._normalise_data = f.readlines()

    # ---------- Normalise Artist name and Track title --

    def normalise(self, title: str, artist: str, featuring: str = None) -> Tuple[str, str, str]:
        new_featuring = [self._normalise_for_compare(featuring)] if featuring else []
        new_title = self._normalise_for_compare(title)
        new_artist = self._normalise_for_compare(artist)

        # replace known phrases that just confuse things
        for find in self._normalise_data:
            new_find = find.casefold().strip()
            if new_find and (new_find in new_title or new_find in new_artist):
                regex = re.compile(r'\b' + new_find + r'\b')
                new_title = regex.sub('', new_title)
                new_artist = regex.sub('', new_artist)

        # extract any featured artists
        # group 1 - full match, group 2 - phrase, group 3 - artist name
        rs = [
            re.compile(r'.*((?:[(\[{])(ft|feat\.|featuring) (.*)(?:[)\]}]+)$)'),
            re.compile(r'.*(\b(ft|feat\.|featuring) (.*)$)'),
        ]
        for r in rs:
            match_title = r.match(new_title)
            if match_title:
                new_title = (new_title[0:match_title.span(1)[0]] + new_title[match_title.span(1)[1]:]).strip()
                new_featuring.append(match_title.group(3))

            match_artist = r.match(new_artist)
            if match_artist:
                new_artist = (new_artist[0:match_artist.span(1)[0]] + new_title[match_artist.span(1)[1]:]).strip()
                new_featuring.append(match_artist.group(3))

        new_artist = new_artist.strip()
        new_title = new_title.strip()
        new_featuring = ', '.join(i.replace(new_artist, '').strip() for i in new_featuring if i).strip()

        return new_title, new_artist, new_featuring

    def _normalise_for_compare(self, value: str) -> str:
        if not value:
            return ''
        chars_all = unicodedata.normalize('NFKD', value)
        chars_not_comb = ''.join([c for c in chars_all if not unicodedata.combining(c)])
        caseless = chars_not_comb.casefold().strip()
        return caseless

    # ---------- Downloading -----------------------------

    def download_text(self, url: str) -> Optional[str]:
        # load from cache
        content = self.cache_load_page(url)
        if content:
            return content

        # get from website
        self._logger.info(f'Downloading text from {url}')
        page = requests.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.text
            self.cache_save_page(url, content)

        if not content:
            return None

        return content

    def download_json(self, url: str) -> Optional[Dict]:
        # load from cache
        content = self.cache_load_object(url)
        if content:
            return content

        # get from website
        self._logger.info(f'Downloading json from {url}')
        page = requests.get(url)
        if page.is_redirect or page.is_permanent_redirect or page.status_code != 200:
            content = None
        else:
            content = page.json()
            self.cache_save_object(url, content)

        if not content:
            return None

        return content

    # ---------- Local Cache -----------------------------

    def cache_item_id(self, url) -> str:
        item_id = ''.join(c if c in self._cache_chars else '' for c in url).strip()
        return item_id.casefold()

    def cache_save_page(self, url, content) -> bool:
        return self._cache_save(url, content)

    def cache_load_page(self, url) -> Optional[str]:
        return self._cache_load(url)

    def cache_save_object(self, key: str, value: Any) -> bool:
        return self._cache_save(key, json.dumps(value), ext='json')

    def cache_load_object(self, key: str):
        value = self._cache_load(key, ext='json')
        if value:
            return json.loads(value)
        return None

    def _cache_save(self, key: str, value: Any, ext: str = 'txt') -> bool:
        if not self._use_cache:
            return False

        makedirs(self._local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(self._local_cache_dir, item_id + '.' + ext)

        self._logger.info(f'Saving cache for {key} to {file_path}')

        with open(file_path, 'wb') as f:
            f.write(value.encode('utf-8'))
        return True

    def _cache_load(self, key: str, ext: str = 'txt') -> Optional[StoredTypes]:
        if not self._use_cache:
            return None

        makedirs(self._local_cache_dir, exist_ok=True)
        item_id = self.cache_item_id(key)
        file_path = join(self._local_cache_dir, item_id + '.' + ext)

        if not isfile(file_path):
            self._logger.warning(f'Could not load cache for {key} from {file_path}')
            return None

        self._logger.info(f'Loading cache for {key} from {file_path}')

        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8')

    # ---------- Select song and build playlist data  -----------------------------

    def select_song(self, song_hits: List[Dict], query_title: str, query_artist: str, query_featuring: str):
        count = len(song_hits)
        self._logger.debug(f'Selecting song from {count} options')

        # if there are songs, then no match
        if count == 0:
            self._logger.warning(f'There were no available songs for "{query_title} - {query_artist}"')
            return {}

        # if there are results, then the query title and artist must appear in the result
        for song in song_hits:
            q_title, q_artist, q_featuring = self.normalise(query_title, query_artist, query_featuring)
            r_title, r_artist, r_featuring = self.normalise(song['track']['title'], song['track']['artist'])
            if self._is_match(q_title, q_artist, q_featuring, r_title, r_artist, r_featuring):
                self._logger.info(f'Selected song "{song["track"]["title"]} - {song["track"]["artist"]}"')
                return song['track']

        # if there are no matches, then no match
        self._logger.warning(f'Did not select a song from {count} results for "{query_title} - {query_artist}"')
        return {}

    def build_result(self, result: Optional[Dict], query: Dict):
        q_title, q_artist, q_featuring = self.normalise(query['title'], query['artist'], query['featuring'])

        selected_title = result.get('title')
        selected_artist = result.get('artist')
        selected_track_id = result.get('storeId') or result.get('trackId') or result.get('id') or result.get('nid')
        r_title, r_artist, r_featuring = self.normalise(selected_title, selected_artist)

        return {
            'track_id': selected_track_id,
            'title': selected_title,
            'artist': selected_artist,
            'match': self._is_match(q_title, q_artist, q_featuring, r_title, r_artist, r_featuring)
        }

    def build_playlist(self, songs_found: Dict[str, Any], songs_missing: Dict[str, Any]) -> Dict[str, Any]:
        found_count = len(songs_found)
        missing_count = len(songs_missing)

        descr_prefix = f'Found {found_count} songs, missing {missing_count}: '
        descr_missing = ', '.join([f'({index}) "{song["title"]} - {song["artist"]}"'
                                   for index, song in songs_missing.items()])
        description = f'{descr_prefix} {descr_missing}.'

        gmusic_song_ids = [None] * (len(songs_missing) + len(songs_found))
        for index, song in songs_found.items():
            gmusic_song_ids[int(index) - 1] = song['gmusic']['track_id']

        return {
            'description': description,
            'gmusic_song_ids': [i for i in gmusic_song_ids if i],
        }

    def _is_match(self, query_title: str, query_artist: str, query_featuring: str, result_title: str,
                  result_artist: str, result_featuring: str):
        if not query_title or not result_title or not query_artist or not result_artist:
            return False

        query_title = query_title.casefold().strip().replace(' ', '')
        query_artist = query_artist.casefold().strip().replace(' ', '')
        query_featuring = query_featuring.casefold().strip().replace(' ', '')
        result_title = result_title.casefold().strip().replace(' ', '')
        result_artist = result_artist.casefold().strip().replace(' ', '')
        result_featuring = result_featuring.casefold().strip().replace(' ', '')

        if query_title in result_title and query_artist == result_artist:
            return True

        if query_artist in result_artist and query_title == result_title:
            return True

        return False
