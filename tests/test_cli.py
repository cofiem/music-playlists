import pathlib

from importlib.resources import files

from click.testing import CliRunner

from music_playlists.cli import music_playlists


def test_no_args():
    runner = CliRunner()
    result = runner.invoke(music_playlists, [])
    assert result.exit_code == 2
    assert "Usage: music-playlists [OPTIONS] COMMAND [ARGS]..." in result.output


def test_list():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp_dir:
        with files("tests.resources").joinpath("test.toml").open('r') as config_path:
            config_content = config_path.read()
            text_config_file = pathlib.Path(tmp_dir, "test.toml")
            text_config_file.write_text(config_content)
            result = runner.invoke(
                music_playlists, ["list", "--config-file", str(text_config_file)]
            )
    assert result.exit_code == 0
    assert "Available Sources and Services" in result.output
