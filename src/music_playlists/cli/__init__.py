import pathlib

import click

from rich.console import Console
from rich.table import Table

from music_playlists import process
from music_playlists.__about__ import __version__
from music_playlists.services import spotify, youtube_music
from music_playlists.sources import abc_radio, last_fm, radio_4zzz


CONFIG_FILE_OPT = {
    "args": ["--config-file"],
    "kwargs": {
        "envvar": "MUSIC_PLAYLISTS_CONFIG_FILE",
        "type": click.Path(),
        "default": pathlib.Path.cwd().joinpath("config.toml"),
    },
}


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
@click.version_option(version=__version__, prog_name="Music Playlists")
def music_playlists():
    """Generates streaming music playlists from various song charts."""


@music_playlists.command("list")
@click.option(*CONFIG_FILE_OPT["args"], **CONFIG_FILE_OPT["kwargs"])
def list_cmd(config_file):
    """List all the music playlist sources and services."""
    p = process.Process(pathlib.Path(config_file))
    rows = p.list_available()

    table = Table(title="Available Sources and Services")
    table.add_column("Title", style="magenta")
    table.add_column("Code", justify="left", style="green")
    table.add_column("Source", justify="left", style="blue")
    table.add_column("Service", justify="left", style="blue")
    table.add_column("Playlist Id", justify="left", style="blue")

    for row in rows:
        table.add_row(
            row.get("title"),
            row.get("code"),
            row.get("source"),
            row.get("service"),
            row.get("playlist_id"),
        )

    console = Console()
    console.print(table)


@music_playlists.group()
def sources():
    """The sources that provide music playlists."""


@sources.command()
@click.argument(
    "code",
    type=click.Choice(
        sorted(
            [
                f"{m.code}-{k}"
                for m in [
                    abc_radio.Manage,
                    last_fm.Manage,
                    radio_4zzz.Manage,
                ]
                for k in m.available().keys()
            ]
        ),
        case_sensitive=False,
    ),
)
@click.option("--refresh", is_flag=True)
@click.option(*CONFIG_FILE_OPT["args"], **CONFIG_FILE_OPT["kwargs"])
def show(config_file, code, refresh):
    """Show all the tracks from the music playlist with CODE."""
    p = process.Process(pathlib.Path(config_file))
    tl = p.source_show(code, refresh)

    # print track list as table
    track_count = len(tl.tracks)
    plural = "track" if track_count == 1 else "tracks"
    table = Table(
        title=f"{tl.title} ({len(tl.tracks)} {plural} - {tl.type.name.lower()})"
    )

    table.add_column("Artist", style="magenta")
    table.add_column("Track", justify="left", style="green")

    for t in tl.tracks:
        table.add_row("; ".join(t.artists), t.title)

    console = Console()
    console.print(table)


@music_playlists.group()
def services():
    """The music services that host streaming music playlists."""


@services.command()
@click.option(
    "--code",
    type=click.Choice(
        sorted(
            [
                f"{m.code}-{k}"
                for m in [
                    abc_radio.Manage,
                    last_fm.Manage,
                    radio_4zzz.Manage,
                ]
                for k in m.available().keys()
            ]
        ),
        case_sensitive=False,
    ),
)
@click.option(
    "--source",
    type=click.Choice(
        sorted(
            [
                m.code
                for m in [
                    abc_radio.Manage,
                    last_fm.Manage,
                    radio_4zzz.Manage,
                ]
            ]
        ),
        case_sensitive=False,
    ),
)
@click.option(
    "--service",
    type=click.Choice(
        sorted(
            [
                m.code
                for m in [
                    spotify.Manage,
                    youtube_music.Manage,
                ]
            ]
        ),
        case_sensitive=False,
    ),
)
@click.option("--refresh", is_flag=True, default=True)
@click.option(*CONFIG_FILE_OPT["args"], **CONFIG_FILE_OPT["kwargs"])
def update(
    config_file,
    code: str | None = None,
    source: str | None = None,
    service: str | None = None,
    refresh: bool = False,
):
    """Update the songs in the playlists."""
    p = process.Process(pathlib.Path(config_file))
    p.services_update(code, source, service, refresh)


if __name__ == "__main__":
    music_playlists()
