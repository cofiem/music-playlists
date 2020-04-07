import logging
import os
import unicodedata
from datetime import datetime
from typing import Dict, Tuple, List, Any

from boltons.strutils import slugify


class PlaylistData:
    _logger = logging.getLogger(__name__)

    def __init__(self, time_zone: datetime.tzinfo):
        self._time_zone = time_zone

    def normalise(self, track: str, artist: str, featuring: str = None) -> Tuple[str, str, str]:
        norm_track = track if track else ''
        norm_artist = artist if artist else ''
        norm_featuring = featuring if featuring else ''

        # normalise text
        norm_track = self._normalise_for_compare(norm_track)
        norm_artist = self._normalise_for_compare(norm_artist)
        norm_featuring = [self._normalise_for_compare(norm_featuring)] if norm_featuring else []

        # extract any featured artists
        norm_track, norm_featuring = self._normalise_featuring(norm_track, norm_featuring)
        norm_artist, norm_featuring = self._normalise_featuring(norm_artist, norm_featuring)

        # remove punctuation
        remove_chars = '[](){},-#=&_'
        for item in remove_chars:
            norm_track = norm_track.replace(item, ' ')
            norm_artist = norm_artist.replace(item, ' ')
            norm_featuring = [i.replace(item, ' ') for i in norm_featuring if i]

        # replace chars
        replace_chars = {
            "’": "'"
        }
        for k, v in replace_chars.items():
            norm_track = norm_track.replace(k, v)
            norm_artist = norm_artist.replace(k, v)
            norm_featuring = [i.replace(k, v) for i in norm_featuring if i]

        # final cleanup - ensure featuring does not contain artist or track
        norm_artist = norm_artist.strip()
        norm_track = norm_track.strip()
        norm_featuring = ' , '.join([i.replace(norm_artist, ' ').replace(norm_track, ' ').strip(', ')
                                     for i in norm_featuring if i])

        return norm_track, norm_artist, norm_featuring

    def _normalise_featuring(self, text: str, featuring: List[str]) -> Tuple[str, List[str]]:
        seps = ['[', ']', '{', '}', ' ft ', ' ft. ', ' feat ', ' feat. ', ' featuring ', ' w/ ', ' x ', ',']
        placeholder1 = ' ->|sep|<- '
        placeholder2 = '->|sep|<-'
        source = text + placeholder1 + placeholder1.join(featuring or [])
        source = source.replace('(', ' ').replace(')', ' ')

        for sep in seps:
            source = source.replace(sep, placeholder1)

        results = source.split(placeholder2)

        # the first item is the text, the rest is the featuring
        norm_text = (results[0] if results else '').strip()
        norm_featuring = list(set(i.strip() for i in results[1:] if i and i.strip() and norm_text.strip() != i.strip()))

        if any(placeholder2 in i for i in norm_featuring):
            raise Exception(f"Feature should not contain separator: '{norm_featuring}'")

        if any('w/' in i for i in norm_featuring):
            a = 1

        return norm_text, norm_featuring

    def _findall(self, p, s):
        """Yields all the positions of
        the pattern p in the string s."""
        i = s.find(p)
        while i != -1:
            yield i
            i = s.find(p, i + 1)

    def _normalise_for_compare(self, value: str) -> str:
        if not value:
            return ''
        chars_all = unicodedata.normalize('NFKD', value)
        chars_not_comb = ''.join([c for c in chars_all if not unicodedata.combining(c)])
        caseless = chars_not_comb.casefold().strip()
        return caseless

    def select_song(self, song_hits: List[Dict], query_title: str, query_artist: str,
                    query_featuring: str) -> Dict[str, Any]:
        count = len(song_hits)
        msg_text = f"'{query_title} - {query_artist}'"

        # if there are songs, then no match
        if count == 0:
            self._logger.warning(f"There were no available songs for {msg_text}")
            return {}

        # if there are results, then the query title and artist must appear in the result
        # order matching by longest first
        song_hits_sorted = sorted(
            song_hits, key=lambda x: len(x['track']['title']) + len(x['track']['artist']), reverse=True)

        for song in song_hits_sorted:
            q_title, q_artist, q_featuring = query_title, query_artist, query_featuring
            r_title, r_artist, r_featuring = self.normalise(song['track']['title'], song['track']['artist'])
            song_match = self._is_match(q_title, q_artist, q_featuring, r_title, r_artist, r_featuring)
            if song_match:
                selected_track_id = song['track'].get('storeId') or \
                                    song['track'].get('trackId') or \
                                    song['track'].get('id') or \
                                    song['track'].get('nid')
                self._logger.debug(f"Selected song for {msg_text} from {count} options: '{r_title} - {r_artist}'")
                return {
                    'track_id': selected_track_id,
                    'title': r_title,
                    'artist': r_artist,
                    'featuring': r_featuring,
                    'match': song_match
                }

        # if there are no matches, then no match
        match_options = [f"{i['track']['title']} - {i['track']['artist']}" for i in song_hits]
        self._logger.warning(f"Did not select a song for {msg_text} from {count} options '{match_options}'")
        return {}

    def build_playlists(self, tracks: List[Dict]) -> List[Dict[str, Any]]:
        current_datetime = datetime.now(tz=self._time_zone)
        self._logger.info('Building playlists')
        playlists = {}
        for track in tracks:
            playlist = track['playlist']
            playlist_title = playlist['title']

            for service_name, service_data in track['services'].items():
                playlist_id = service_data.get('playlist_id')
                match = service_data.get('match')
                track_id = service_data.get('track_id')
                playlist_code = f"{playlist_title}-{service_name}"

                if playlist_code not in playlists:
                    playlists[playlist_code] = {
                        'title': playlist_title,
                        'display_name': f"{playlist_title} ({current_datetime.strftime('%a, %d %b %Y')})",
                        'playlist_id': os.getenv(playlist_id) if playlist_id else None,
                        'description': '',
                        'tracks_missing': 0,
                        'tracks_included': 0,
                        'tracks_total': 0,
                        'tracks': [],
                        'service': service_name
                    }
                    self._logger.info(f"Added playlist '{playlist_title}' for service '{service_name}'")

                playlists[playlist_code]['tracks_total'] += 1

                if match is True and track_id:
                    playlists[playlist_code]['tracks_included'] += 1
                    playlists[playlist_code]['tracks'].append(track_id)
                else:
                    playlists[playlist_code]['tracks_missing'] += 1

                # create the description
                tracks_included = playlists[playlist_code]['tracks_included']
                tracks_missing = playlists[playlist_code]['tracks_missing']
                tracks_total = playlists[playlist_code]['tracks_total']
                tracks_percent = float(tracks_included) / float(tracks_total)
                playlists[playlist_code]['description'] = \
                    f"This playlist is generated each day. " \
                    f"There are {tracks_included} songs of {tracks_total} ({tracks_percent:.0%}). " \
                    f"Couldn't find {tracks_missing} songs. " \
                    "For more information: https://github.com/cofiem/music-playlists"

        self._logger.info('Completed playlists')
        return list(playlists.values())

    def _is_match(self, query_title: str, query_artist: str, query_featuring: str, result_title: str,
                  result_artist: str, result_featuring: str):
        if not query_title or not result_title or not query_artist or not result_artist:
            return False

        query_title = self._make_slug(query_title, sep='')
        query_artist = self._make_slug(query_artist, sep='')
        query_featuring = self._make_slug(query_featuring, sep='')
        result_title = self._make_slug(result_title, sep='')
        result_artist = self._make_slug(result_artist, sep='')
        result_featuring = self._make_slug(result_featuring, sep='')

        match_title = query_title in result_title
        match_artist = query_artist in result_artist
        match_featuring = query_featuring in result_featuring
        match_featuring2 = result_featuring in query_featuring

        equal_title = query_title == result_title
        equal_artist = query_artist == result_artist
        equal_featuring = query_featuring == result_featuring

        has_featuring = query_featuring and result_featuring

        # these are the variations that are valid
        if equal_title and equal_artist and match_featuring and has_featuring:
            return True
        if match_title and equal_artist and match_featuring and not has_featuring:
            return True
        if equal_title and equal_artist and has_featuring and (match_featuring or match_featuring2):
            return True

        return False

    def _make_slug(self, value: str, sep: str = '-'):
        return slugify(value, delim=sep, ascii=True).decode('utf-8')
