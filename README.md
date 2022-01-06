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

## Dependencies

- python = "^3.8"
- typer = "^0.4.0"
- feedparser = "^6.0.8"
- beautifulsoup4 = "^4.10.0"
- requests = "^2.27.0"

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
