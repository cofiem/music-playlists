import logging

from beartype import beartype

from music_playlists.process import Process
from beartype.claw import beartype_package

beartype_package("music_playlists")
logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("requests_cache").setLevel(logging.INFO)


@beartype
def main():
    p = Process()
    p.run()


if __name__ == "__main__":
    main()
