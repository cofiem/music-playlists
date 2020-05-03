# Music Playlists

Generates playlists for streaming music services from various song charts.

[![CircleCI](https://circleci.com/gh/cofiem/music-playlists/tree/master.svg?style=svg)](https://circleci.com/gh/cofiem/music-playlists/tree/master)

## Playlists

### Triple J Unearthed Weekly

- [Playlist Source](https://www.triplejunearthed.com/discover/charts)
- [Generated Google Music Playlist](https://play.google.com/music/playlist/AMaBXykfhR3K2N58JDfwGMt4-CHPpR21_sybQveOb2g5vnmXPoL2RxuJSnXwDBv_a0BhN3eT7Iy1QRkVtcIzuB79oTrkvfbOBA%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/1Fi0e7Bwof3ZZYKiTqIFeG?si=oRAHLVk_RCiuHfIPOBwQow)
- [Similar Spotify Playlist by Triple J](https://open.spotify.com/playlist/78d1cKN9xYtKialnOYkI92?si=oplGx5CuRpO2sTUiQnrDsQ)

### Triple J Most Played Daily

- [Playlist Source](https://www.abc.net.au/triplej/featured-music/most-played/)
- [Generated Google Music Playlist](https://play.google.com/music/playlist/AMaBXymNn6HXtD6yk3Jw7NCw-bWtU3KfqtGNEvF7zGuzopDBEWO0ZDkiRdH2ryGRNMACIf_jfcHgBlvaU3_yDE1ZLRC8HZi-nA%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/6fk0j4ncAVZgR0BGXgnoQP?si=-MikM58CSIuVclL2fJT5ag)
- [Similar Spotify Playlist by Triple J](https://open.spotify.com/playlist/7vFQNWXoblEJXpbnTuyz76?si=Tvc6fZQYSbqJf6LL2HsgnA)

### Double J Most Played Daily

- [Playlist Source](https://www.abc.net.au/doublej/featured-music/most-played/)
- [Generated Google Music Playlist](https://play.google.com/music/playlist/AMaBXyngnVFOVBFpxZS2b8M3DTQk8Ub9aUoSaohDL0UsE00z_Y-2H7_KuX1u_Cy7QTnCUPDVTXSlSSXoJS4sVVpOmnKJXDZwBQ%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/5pMHkM6y47xeqKstXTxe5l?si=lDCE4P0nTOiyfF5AaNiCig)
- [Similar Spotify Playlist by Double J](https://open.spotify.com/playlist/3eVaP90RyWrOKu6Gejw5Eg?si=qitVGp0PQJ-8wm92WTacqg)

### Radio 4zzz Weekly

- [Playlist Source](http://4zzz.org.au/)
- [Generated Google Music Playlist](https://play.google.com/music/playlist/AMaBXylJ3xayO9dRNgmyQazXw2KEEfiFLML8UtMng0v0lSpZRinG_1qz994rPPOc5sBDkN4QDLMxbWAZHtKMPmmfYyabzQ3SMQ%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/6QXfh1GEnk5WZcgk6DYeFX?si=uAW1Ui8qRN6uF_H2p4rJGQ)

### Last.fm Most Popular Weekly

- [Playlist Source](https://www.last.fm/charts)
- [Generated Google Music Playlist](https://play.google.com/music/listen?u=0#/pl/AMaBXymCyYTfzBUMrhxu-gmv105W0p50bursBWRXeH3KlPeAGdBsrsth4wfAd_gJo1RK0BWRcO1fCmrwTazI5_WQsLn4xpzQKQ%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/2OG0mxQqwQ4y26f7lrFv7z?si=GcMN5TDASjm_tG0N5vaG6A)

### SoundCloud Trending Australia Weekly

- [Playlist Source](https://soundcloud.com/charts/new?genre=all-music&country=AU)
- [Generated Google Music Playlist](https://play.google.com/music/listen?u=0#/pl/AMaBXym36AMhKosMhuNHEZugZB9Vmcp4H6X_gH22EBufF0_gWunMqjeZR7SiHVouyccPFUnCEygbxFutkRbUKhl0hIjhCUamRw%3D%3D)
- [Generated Spotify Playlist](https://open.spotify.com/playlist/5nBtYkUuLlbfOWc0Jy4s2E?si=dedwtEUeTxaFQCQM_8db1A)


## Script Setup

The script requires some environment variables to run.

### Google Music

- `GOOGLE_MUSIC_AUTH_DEVICE_ID` - the device id from running gmusicapi 
    [`Mobileclient.perform_oauth`](https://unofficial-google-music-api.readthedocs.io/en/latest/reference/mobileclient.html#gmusicapi.clients.Mobileclient.perform_oauth)
- `GOOGLE_MUSIC_AUTH_CONFIG` - the contents of the mobileclient config file
- The Google Music playlist ids:
    - `GOOGLE_MUSIC_PLAYLIST_ID_TRIPLEJ_UNEARTHED`
    - `GOOGLE_MUSIC_PLAYLIST_ID_TRIPLEJ_MOST_PLAYED`
    - `GOOGLE_MUSIC_PLAYLIST_ID_DOUBLEJ_MOST_PLAYED`
    - `GOOGLE_MUSIC_PLAYLIST_ID_RADIO_4ZZZ_MOST_PLAYED`
    - `GOOGLE_MUSIC_PLAYLIST_ID_LASTFM_MOST_POPULAR_AUS`
    - `GOOGLE_MUSIC_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS`


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
    - `SPOTIFY_PLAYLIST_ID_SOUNDCLOUD_TRENDING_AUS`


### Last.fm

- `LASTFM_AUTH_API_KEY` - the Last.fm [API Key](https://www.last.fm/api/)


### SoundCloud

- `SOUNDCLOUD_CLIENT_ID` - the SoundCloud [App Client Id](https://soundcloud.com/you/apps)


## Development

Local development can require running the script multiple times in quick succession. 
This is not a great thing to do for web services. There is the possibility to cache output for each class.

Change the cache setting in the Downloader in `main.py`.

With thanks to Simon Weber for [gmusicapi](https://github.com/simon-weber/gmusicapi).
