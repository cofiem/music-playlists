FROM python:3.14@sha256:6d58c1a9444bc2664f0fa20c43a592fcdb2698eb9a9c32257516538a2746c19a

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
