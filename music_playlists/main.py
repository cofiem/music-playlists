import logging

from music_playlists.process import Process

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
    level=logging.INFO,
)


def main():
    p = Process()
    p.run()


if __name__ == "__main__":
    main()
