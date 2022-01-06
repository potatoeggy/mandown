# mandown

<p align="center">
    <img src="https://img.shields.io/pypi/v/mandown" />
    <img src="https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag" />
    <img src="https://img.shields.io/github/issues/potatoeggy/mandown" />
    <img src="https://img.shields.io/github/forks/potatoeggy/mandown" />
    <img src="https://img.shields.io/github/stars/potatoeggy/mandown" />
    <img src="https://img.shields.io/github/license/potatoeggy/mandown" />
</p>

Python library and command line application to download books from various sources including manga

Currently only supports MangaSee.

## Installation

Install the package from PyPI:

```
pip install mandown
```

Or, to build from source:

```
git clone https://github.com/potatoeggy/mandown.git
poetry install
poetry build
```

## Usage

```
mandown URL DESTINATION_FOLDER
```

Run `python cli.py --help` for more info.

## Library usage

```python
from mandown import mandown

md.download(url_to_manga, destination_folder, start_chapter=None, end_chapter=None, maxthreads=4)

manga = md.query(url_to_manga)
print(manga.metadata, manga.chapters)
```
