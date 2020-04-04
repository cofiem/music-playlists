# Music Playlists

Generates playlists for streaming music services from various song charts.

[![CircleCI](https://circleci.com/gh/cofiem/music-playlists/tree/master.svg?style=svg)](https://circleci.com/gh/cofiem/music-playlists/tree/master)

## Playlists

### Triple J Unearthed Weekly

- Source - [Website](https://www.triplejunearthed.com/discover/charts)
- Generated playlist - 
    [Google Music](https://play.google.com/music/playlist/AMaBXykfhR3K2N58JDfwGMt4-CHPpR21_sybQveOb2g5vnmXPoL2RxuJSnXwDBv_a0BhN3eT7Iy1QRkVtcIzuB79oTrkvfbOBA%3D%3D)
- A similar playlist maintained by Triple J - 
    [Spotify Url](https://open.spotify.com/playlist/78d1cKN9xYtKialnOYkI92?si=oplGx5CuRpO2sTUiQnrDsQ)

### Triple J Most Played Daily

- Source - [Website](https://www.abc.net.au/triplej/featured-music/most-played/)
- Generated playlist - 
    [Google Music](https://play.google.com/music/playlist/AMaBXymNn6HXtD6yk3Jw7NCw-bWtU3KfqtGNEvF7zGuzopDBEWO0ZDkiRdH2ryGRNMACIf_jfcHgBlvaU3_yDE1ZLRC8HZi-nA%3D%3D)
- A similar playlist maintained by Triple J - 
    [Spotify Url](https://open.spotify.com/playlist/7vFQNWXoblEJXpbnTuyz76?si=Tvc6fZQYSbqJf6LL2HsgnA)

### Double J Most Played Daily

- Source - [Website](https://www.abc.net.au/doublej/featured-music/most-played/)
- Generated playlist - 
    [Google Music](https://play.google.com/music/playlist/AMaBXyngnVFOVBFpxZS2b8M3DTQk8Ub9aUoSaohDL0UsE00z_Y-2H7_KuX1u_Cy7QTnCUPDVTXSlSSXoJS4sVVpOmnKJXDZwBQ%3D%3D)
- A similar playlist maintained by Double J - 
    [Spotify Url](https://open.spotify.com/playlist/3eVaP90RyWrOKu6Gejw5Eg?si=qitVGp0PQJ-8wm92WTacqg)

### Radio 4zzz Weekly

- Source - [Website](http://4zzz.org.au/)
- Generated playlist - 
    [Google Music](https://play.google.com/music/playlist/AMaBXynHjqCUVHudGshhOIYUnwqDp_xZwF6Kg8U1fOpd-T90-V6xMC9HMlQ7h9AjZylAipR7QKMxOJWxtePR4cz8VezjIpONpw%3D%3D)


## Script Setup

The script requires some environment variables to run:

- `GMUSICAPI_DEVICE_ID` - the device id from running gmusicapi 
    [`Mobileclient.perform_oauth`](https://unofficial-google-music-api.readthedocs.io/en/latest/reference/mobileclient.html#gmusicapi.clients.Mobileclient.perform_oauth)
- `GMUSIC_CONFIG` - the contents of the mobileclient config file
- The Google Music playlist ids:
    - `GOOGLE_MUSIC_PLAYLIST_TRIPLEJ_UNEARTHED_ID`
    - `GOOGLE_MUSIC_PLAYLIST_TRIPLEJ_MOST_PLAYED_ID`
    - `GOOGLE_MUSIC_PLAYLIST_DOUBLEJ_MOST_PLAYED_ID`
    - `GOOGLE_MUSIC_PLAYLIST_RADIO_4ZZZ_MOST_PLAYED_ID`

## Development

Local development can require running the script multiple times in quick succession. 
This is not a great thing to do for web services. There is the possibility to cache output for each class.

Change the cache setting in the Downloader in `main.py`.

With thanks to Simon Weber for [gmusicapi](https://github.com/simon-weber/gmusicapi).

## TODO

Implement generating spotify playlists. Pick one of these packages:
- https://github.com/omarryhan/pyfy#quick-start
- https://github.com/felix-hilden/spotipy#retrieving-an-access-token
- https://github.com/Harrison97/spotipy/blob/master/docs/index.rst
- https://github.com/Saphyel/spotify-api
