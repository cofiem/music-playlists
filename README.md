# Music Playlists

Generates playlists for streaming music services from various song charts.

[![CircleCI](https://circleci.com/gh/cofiem/music-playlists.svg?style=svg)](https://circleci.com/gh/cofiem/music-playlists)

## Playlists

- [Triple J Unearthed Weekyl Chart Top 100](https://www.triplejunearthed.com/discover/charts)
    - [Google Music](https://play.google.com/music/playlist/AMaBXykfhR3K2N58JDfwGMt4-CHPpR21_sybQveOb2g5vnmXPoL2RxuJSnXwDBv_a0BhN3eT7Iy1QRkVtcIzuB79oTrkvfbOBA%3D%3D)
    - Spotify (TODO)
- [Triple J Most Played Daily Top 50](https://www.abc.net.au/triplej/featured-music/most-played/)
    - [Google Music](https://play.google.com/music/playlist/AMaBXymNn6HXtD6yk3Jw7NCw-bWtU3KfqtGNEvF7zGuzopDBEWO0ZDkiRdH2ryGRNMACIf_jfcHgBlvaU3_yDE1ZLRC8HZi-nA%3D%3D)
    - Spotify (TODO)
- [Double J Most Played Daily Top 50](https://www.abc.net.au/doublej/featured-music/most-played/)
    - [Google Music](https://play.google.com/music/listen?u=0#/pl/AMaBXyngnVFOVBFpxZS2b8M3DTQk8Ub9aUoSaohDL0UsE00z_Y-2H7_KuX1u_Cy7QTnCUPDVTXSlSSXoJS4sVVpOmnKJXDZwBQ%3D%3D)
    - Spotify (TODO)

## Setup

The script requires some environment variables to run:

- `GMUSICAPI_DEVICE_ID` - the device id from running gmusicapi [`Mobileclient.perform_oauth`](https://unofficial-google-music-api.readthedocs.io/en/latest/reference/mobileclient.html#gmusicapi.clients.Mobileclient.perform_oauth)
- `MUSIC_SOURCE_TRIPLEJ_UNEARTHED_PLAYLIST_ID` - the Google Music playlist UUID for the "Triple J Unearthed Weekyl Chart Top 100"
- `MUSIC_SOURCE_TRIPLEJ_MOST_PLAYED_PLAYLIST_ID` - the Google Music playlist UUID for the "Triple J Most Played Daily Top 50"
- `MUSIC_SOURCE_DOUBLEJ_MOST_PLAYED_PLAYLIST_ID` - the Google Music playlist UUID for the "Double J Most Played Daily Top 50"

To run on a CI service requires some additional environment variables:

- `GMUSIC_CONFIG` - the contents of the config file (found in `/home/<user>/.local/share/gmusicapi/mobileclient.cred`)


## Development

Local development can require running the script multiple times in quick succession. 
This is not a great thing to do for web services. There is the possibility to cache output for each class.
