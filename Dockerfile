FROM python:3.12@sha256:3db5aa189b01efbd46596c63c958064b72c8de01f199fb14c9ae2118c40633de

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
