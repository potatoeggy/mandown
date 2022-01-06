# mandown

<p align="center">
    <a href="https://pypi.org/project/mandown"><img src="https://img.shields.io/pypi/v/mandown" /></a>
    <a href="https://github.com/potatoeggy/mandown/releases/latest"><img src="https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag" /></a>
    <a href="https://github.com/potatoeggy/mandown/issues"><img src="https://img.shields.io/github/issues/potatoeggy/mandown" /></a>
    <a href="/LICENSE"><img src="https://img.shields.io/github/license/potatoeggy/mandown" /></a>
    <img src="https://img.shields.io/github/forks/potatoeggy/mandown" /></a>
    <img src="https://img.shields.io/github/stars/potatoeggy/mandown" />
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
