FROM python:3.14@sha256:6942ebef735aad5f708ef9c5e750cbe37dbc7751cee35c140e33764e34843ab9

RUN python -m pip install hatch

RUN mkdir /opt/music-playlists
WORKDIR /opt/music-playlists

COPY . /opt/music-playlists
RUN echo "MUSIC_PLAYLISTS_TIME_ZONE = 'Australia/Brisbane'" >> .env.toml && \
    echo "MUSIC_PLAYLISTS_BASE_PATH = '.'" >> .env.toml && \
    echo "LASTFM_AUTH_API_KEY = 'not-set'" >> .env.toml && \
    cat .env.toml && \
    pwd && \
    ls -la

RUN hatch run cov
