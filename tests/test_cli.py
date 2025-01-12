import os

import pytest
from click.testing import CliRunner

from music_playlists.cli import music_playlists


@pytest.mark.skipif(
    os.getenv("MUSIC_PLAYLISTS_TESTS_SLOW") != "true", reason="Requires internet access"
)
@pytest.mark.parametrize(
    "name,title",
    [
        ("abc-radio-classic", "ABC Classic Recently Played"),
        ("abc-radio-doublej", "ABC Double J Most Played Daily"),
        ("abc-radio-jazz", "ABC Jazz Recently Played"),
        ("abc-radio-triplej", "ABC Triple J Most Played Daily"),
        ("abc-radio-unearthed", "ABC Triple J Unearthed Weekly"),
        ("last-fm", "Last.fm Most Popular Weekly in Australia"),
        ("radio-4zzz", "4zzz Most Played Weekly"),
    ],
)
def test_sources_run_all(name, title):
    runner = CliRunner()
    result = runner.invoke(music_playlists, ["sources", "run", name])
    assert result.exit_code == 0
    assert title in result.output


@pytest.mark.parametrize(
    "name,title",
    [
        ("abc-radio-classic", "ABC Classic Recently Played"),
    ],
)
def test_sources_run_one(name, title):
    runner = CliRunner()
    result = runner.invoke(music_playlists, ["sources", "run", name])
    assert result.exit_code == 0
    assert title in result.output


@pytest.mark.skipif(
    os.getenv("MUSIC_PLAYLISTS_TESTS_SLOW") != "true", reason="Requires internet access"
)
def test_services_update():
    runner = CliRunner()
    result = runner.invoke(music_playlists, ["services", "update"])
    assert result.exit_code == 0
    assert result.output == ""
