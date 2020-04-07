import logging
from datetime import datetime, timedelta
from typing import Any, List, Dict

from boltons.strutils import slugify

from music_playlists.downloader import Downloader


class Radio4zzzMostPlayed:
    _logger = logging.getLogger(__name__)

    available = [
        {
            'title': '4zzz Most Played Weekly',
            'gmusic_playlist_id': 'GOOGLE_MUSIC_PLAYLIST_RADIO_4ZZZ_MOST_PLAYED_ID',
        }
    ]

    def __init__(self, downloader: Downloader, time_zone: datetime.tzinfo):
        self._downloader = downloader
        self._url = 'https://airnet.org.au/rest/stations/4ZZZ/programs'
        self._time_zone = time_zone

    def run(self, playlist_data: Dict[str, str]):
        self._logger.info(f"Started '{playlist_data['title']}'")

        current_time = datetime.now(tz=self._time_zone)
        date_from = current_time - timedelta(days=7)
        date_to = current_time

        programs = self._downloader.download_json(self._url)

        programs_with_recent_episodes = set()
        tracks = {}
        for program in programs:
            if program.get('archived'):
                continue
            program_name = program['name']

            episodes_url = f"{program['programRestUrl']}/episodes"
            episodes = self._downloader.download_json(episodes_url)
            for episode in (episodes or []):
                episode_start = datetime.strptime(episode['start'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=self._time_zone)
                episode_end = datetime.strptime(episode['end'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=self._time_zone)
                if date_from > episode_start or date_to < episode_start or date_from > episode_end or date_to < episode_end:
                    continue

                programs_with_recent_episodes.add(program_name)

                playlist_url = f"{episode['episodeRestUrl']}/playlists"
                playlist = self._downloader.download_json(playlist_url)
                for track in (playlist or []):
                    track_type = track['type']
                    track_id = track['id']
                    track_artist = track['artist']
                    track_title = track['title']
                    track_track = track['track']
                    track_release = track['release']
                    track_time = track['time']
                    track_notes = track['notes']
                    track_twitter = track['twitterHandle']
                    track_content = track['contentDescriptors']
                    track_is_australian = track_content['isAustralian']
                    track_is_local = track_content['isLocal']
                    track_is_female = track_content['isFemale']
                    track_is_indigenous = track_content['isIndigenous']
                    track_is_new = track_content['isNew']
                    track_wikipedia = track['wikipedia']
                    track_image = track['image']
                    track_video = track['video']
                    track_url = track['url']
                    track_approximate_time = track['approximateTime']

                    if track_type != 'track':
                        raise Exception(f"Track type is expected to be 'track', but is {track_type}.")

                    if track_title != track_track:
                        raise Exception(
                            f"Title and track are expected to match, but do not: '{track_title}' != '{track_track}'")

                    item = {
                        'type': track_type,
                        'id': track_id,
                        'artist': track_artist,
                        'title': track_title,
                        'track': track_track,
                        'release': track_release,
                        'time': track_time,
                        'notes': track_notes,
                        'twitter': track_twitter,
                        'content': track_content,
                        'is_australian': track_is_australian,
                        'is_local': track_is_local,
                        'is_female': track_is_female,
                        'is_indigenous': track_is_indigenous,
                        'is_new': track_is_new,
                        'wikipedia': track_wikipedia,
                        'image': track_image,
                        'video': track_video,
                        'url': track_url,
                        'approximate_time': track_approximate_time,
                        'program_name': program_name,
                        'episode_start': episode_start,
                    }

                    track_key = '-'.join([
                        slugify(track_artist, delim='-', ascii=True).decode('utf-8'),
                        slugify(track_track, delim='-', ascii=True).decode('utf-8')
                    ])
                    if track_key in tracks:
                        tracks[track_key].append(item)
                    else:
                        tracks[track_key] = [item]

        most_played_tracks = sorted([(len(v), k, v) for k, v in tracks.items() if len(v) > 1], reverse=True)

        result = []
        for index, most_played_track in enumerate(most_played_tracks):
            item = {
                'playlist': playlist_data,
                'retrieved_at': current_time,
                'order': index + 1,
                'track': self._choose_value([i['track'] for i in most_played_track[2]]),
                'artist': self._choose_value([i['artist'] for i in most_played_track[2]]),
                'track_id': most_played_track[1],
                'featuring': '',
                'services': {},
                'extra': {
                    'is_australian': self._choose_value([i['is_australian'] for i in most_played_track[2]]),
                    'is_local': self._choose_value([i['is_local'] for i in most_played_track[2]]),
                    'is_female': self._choose_value([i['is_female'] for i in most_played_track[2]]),
                    'is_indigenous': self._choose_value([i['is_indigenous'] for i in most_played_track[2]]),
                    'is_new': self._choose_value([i['is_new'] for i in most_played_track[2]]),
                    'releases': {i['release'] for i in most_played_track[2] if i['release']} or None,
                    'notes': {i['notes'] for i in most_played_track[2] if i['notes']} or None,
                    'twitters': {i['twitter'] for i in most_played_track[2] if i['twitter']} or None,
                    'wikipedias': {i['wikipedia'] for i in most_played_track[2] if i['wikipedia']} or None,
                    'images': {i['image'] for i in most_played_track[2] if i['image']} or None,
                    'videos': {i['video'] for i in most_played_track[2] if i['video']} or None,
                    'urls': {i['url'] for i in most_played_track[2] if i['url']} or None,
                    'program_names': {i['program_name'] for i in most_played_track[2] if i['program_name']} or None,
                }
            }
            result.append(item)

        self._logger.info(f"Completed {playlist_data['title']}")
        return result

    def _choose_value(self, values: List[Any]) -> Any:
        gathered = {}
        for value in values:
            if value is None:
                continue
            if value not in gathered:
                gathered[value] = 1
            else:
                gathered[value] += 1
        values_sorted = sorted([(v, k) for k, v in gathered.items()], reverse=True)
        return values_sorted[0][1] if values_sorted else None
