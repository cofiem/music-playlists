import click
from rich.console import Console
from rich.table import Table

from music_playlists import process
from music_playlists.__about__ import __version__
from music_playlists.sources import abc_radio, last_fm, radio_4zzz


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="Music Playlists")
def music_playlists():
    pass


@music_playlists.group()
def sources():
    pass


@sources.command()
@click.argument(
    "name",
    type=click.Choice(
        sorted(
            [
                *abc_radio.Manage.available_codes.keys(),
                *last_fm.Manage.available_codes.keys(),
                *radio_4zzz.Manage.available_codes.keys(),
            ]
        ),
        case_sensitive=False,
    ),
)
def run(name):
    p = process.Process()
    tl = p.source_run(name)

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
    pass


@services.command()
def update():
    p = process.Process()
    p.services_update()


if __name__ == "__main__":
    music_playlists()
