# Music Playlists

Generates streaming music playlists create from various song charts.

## Playlists

### Triple J Unearthed Weekly

[Playlist Source](https://www.triplejunearthed.com/discover/charts)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflWEJroa8S-ICu4YNzVFQiVl)
- [Similar YouTube Music Playlist](https://music.youtube.com/playlist?list=PLFqO_oqoHHMwqcf99e0zeht2Gm0eOmrQx)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/1Fi0e7Bwof3ZZYKiTqIFeG)
- [Similar Spotify Playlist by Triple J](https://open.spotify.com/playlist/78d1cKN9xYtKialnOYkI92)

### Triple J Most Played Daily

[Playlist Source](https://www.abc.net.au/triplej/featured-music/most-played/)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflXb3R7YIKDtJf015kzwSocB)
- [Similar YouTube Music Playlist](https://music.youtube.com/playlist?list=PLFqO_oqoHHMw8xPXfm2-SOrwXPEHSqoOf)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/6fk0j4ncAVZgR0BGXgnoQP)
- [Similar Spotify Playlist by Triple J](https://open.spotify.com/playlist/7vFQNWXoblEJXpbnTuyz76)

### Double J Most Played Daily

[Playlist Source](https://www.abc.net.au/doublej/featured-music/most-played/)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflUUImfAqq7Y5kxliC5MZz8C)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/5pMHkM6y47xeqKstXTxe5l)
- [Similar Spotify Playlist by Double J](https://open.spotify.com/playlist/3eVaP90RyWrOKu6Gejw5Eg)

### Radio 4zzz Weekly

[Playlist Source](http://4zzz.org.au/)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflVHDZXI5t0RV0zCl0kdYxTq)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/6QXfh1GEnk5WZcgk6DYeFX)

### Last.fm Most Popular Weekly

[Playlist Source](https://www.last.fm/charts)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflWOVUsXTbIezz7JKWbvDU14)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/2OG0mxQqwQ4y26f7lrFv7z)

### SoundCloud Trending Australia Weekly

Not available due to [Soundcloud closing access to API keys](https://github.com/soundcloud/api).

[Playlist Source](https://soundcloud.com/charts/new?genre=all-music&country=AU)

YouTube Music

- [Generated YouTube Music Playlist](https://music.youtube.com/playlist?list=PLxYyVSBSlflVpfo0OvLXqvoynQMHon0ve)

Spotify

- [Generated Spotify Playlist](https://open.spotify.com/playlist/5nBtYkUuLlbfOWc0Jy4s2E)

### Other playlists

- [Guardian Australia Monthly New Music](https://www.theguardian.com/music/series/australias-best-new-music):
  [Spotify](https://open.spotify.com/playlist/5Cw9qgG1EaqvJYYdhGC8JJ)

## Script Setup

The script requires some environment variables to run.

- `PLAYLIST_TIME_ZONE` - Set the time zone for dates, particularly the generated playlists.

### YouTube Music

- `YOUTUBE_MUSIC_AUTH_CONFIG` - the contents of the `headers_auth.json` config file 
  from [these instructions](https://ytmusicapi.readthedocs.io/en/latest/setup.html)
- The YouTube Music playlist ids:
    - `YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_UNEARTHED`
    - `YOUTUBE_MUSIC_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED`
    - `YOUTUBE_MUSIC_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED`
    - `YOUTUBE_MUSIC_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED`
    - `YOUTUBE_MUSIC_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS`


### Spotify

- `SPOTIFY_AUTH_REFRESH_TOKEN` - the refresh token obtained from `Spotify.login_init`
- `SPOTIFY_AUTH_CLIENT_ID` - the client id from the [dashboard](https://developer.spotify.com/dashboard/applications)
- `SPOTIFY_AUTH_CLIENT_SECRET` - the client secret from the [dashboard](https://developer.spotify.com/dashboard/applications)
from the `/authorize` endpoint
- The Spotify playlist ids:
    - `SPOTIFY_PLAYLIST_ID_TRIPLEJ_UNEARTHED`
    - `SPOTIFY_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED`
    - `SPOTIFY_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED`
    - `SPOTIFY_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED`
    - `SPOTIFY_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS`


### Last.fm

- `LASTFM_AUTH_API_KEY` - the Last.fm [API Key](https://www.last.fm/api/)

## Development

Local development can require running the script multiple times in quick succession. 
This is not a great thing to do for web services. There is the possibility to cache output for each class.

Change the cache setting in the Downloader in `main.py`.

With thanks to sigma67 for [ytmusicapi](https://github.com/sigma67/ytmusicapi).
