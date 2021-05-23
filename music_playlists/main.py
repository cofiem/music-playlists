import logging
from argparse import ArgumentParser


from music_playlists.process import Process

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
    level=logging.INFO,
)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate playlists.",
    )
    parser.add_argument(
        "activity",
        choices=["generate", "init"],
        help="the activity to run",
    )
    args = parser.parse_args()

    processing = Process()
    if args.activity == "generate":
        processing.run(processing.default_settings)
    elif args.activity == "init":
        processing.initialise(processing.default_settings)
