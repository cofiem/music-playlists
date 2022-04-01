import logging

from music_playlists.process import Process

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
    level=logging.INFO,
)


if __name__ == "__main__":
    p = Process()
    p.run()
