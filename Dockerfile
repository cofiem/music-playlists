FROM python:3.12@sha256:154f46575bab3aaa3a77cb2a00cfcc195efd1d396f02c82809d51db4ebbc13e6

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
