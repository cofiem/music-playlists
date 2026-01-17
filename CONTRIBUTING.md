# Contributing guide

## Development

Install `hatch`, e.g.

```bash
pipx install hatch
```

## Run tests and linters

Run the tests and linters with multiple python versions.

To run using all available python versions:

```bash
hatch run all:test
```

To run using a particular Python version available in the hatch matrix:

```bash
hatch run +py=3.12 all:test
```

## Test a release locally

Generate the distribution package archives.

```bash
hatch build
```

Generate the docs.

```bash
hatch run docs:build
```

Then create a new virtual environment, install the dependencies, and install from the local wheel.

```bash
rm -rf .venv-test
python -m venv .venv-test
source .venv-test/bin/activate

python -m pip install --upgrade pip

pip install dist/*.whl
```

## Test the installed package

```bash
music-playlists --version
music-playlists --help

```


## Test a release from Test PyPI

If the package seems to work as expected, push changes to the `main` branch.

The `pypi-package.yml` GitHub Actions workflow will deploy a release to Test PyPI.

Then follow the same process as testing a release locally, 
except download the wheel from Test PyPI instead of using the local wheel file.

Go to the [test project page](https://test.pypi.org/project/music-playlists) and check that it looks ok.

## Create a release to PyPI

Create a tag on the `main` branch.

The `pypi-package.yml` GitHub Actions workflow will deploy a release to PyPI.

Go to the [live project page](https://pypi.org/project/music-playlists) and check that it looks ok.

Done!
