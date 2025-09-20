FROM python:3.12@sha256:1cb6108b64a4caf2a862499bf90dc65703a08101e8bfb346a18c9d12c0ed5b7e

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
