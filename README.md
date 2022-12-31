# mandown

![Supported Python versions](https://img.shields.io/pypi/pyversions/mandown)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Download from PyPI](https://img.shields.io/pypi/v/mandown)](https://pypi.org/project/mandown)
[![Download from the AUR](https://img.shields.io/aur/version/mandown-git)](https://aur.archlinux.org/packages/mandown-git)
[![Latest release](https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag)](https://github.com/potatoeggy/mandown/releases/latest)
[![License](https://img.shields.io/github/license/potatoeggy/mandown)](/LICENSE)

Mandown is a comic downloader and converter to CBZ, EPUB, and/or PDF. It also supports image post-processing to make them more readable on certain devices similarly to [KCC](https://github.com/ciromattia/kcc).

## Features

- Download comics from supported sites
  - Supports downloading a range of chapters
  - Supports multithreaded downloading
- Process downloaded images
  - Rotate or split double-page spreads
  - Trim borders
  - Resize images
- Convert downloaded comics to CBZ, EPUB, or PDF

## Supported sites

To request a new site, please file a [new issue](https://github.com/potatoeggy/mandown/issues/new?title=Source%20request:).

- https://mangasee123.com
- https://manganato.com
- https://webtoons.com
- https://mangadex.org
- https://mangakakalot.com
- https://readcomiconline.li

## Installation

Install the package from PyPI:

```
pip3 install mandown
```

Install the optional large dependencies for some features of Mandown:
```
# image processing
pip3 install Pillow

# graphical interface (GUI)
pip3 install PySide6
```

Arch Linux users may also install the package from the [AUR](https://aur.archlinux.org/packages/mandown-git):

```
git clone https://aur.archlinux.org/mandown-git.git
makepkg -si
```

Or, to build from source:

Mandown depends on [poetry](https://github.com/python-poetry/poetry) for building.

```
git clone https://github.com/potatoeggy/mandown.git
poetry install
poetry build
pip3 install dist/mandown*.whl
```

## Basic usage

See the [docs](/docs/) for more information and examples.

```
mandown get <URL>
```

To convert the download contents to CBZ/EPUB/PDF, append the `--convert` option. To apply image processing to the downloaded images, append the `--process` option.

```
mandown get <URL> --convert epub --process rotate_double_pages
```

To download only a certain range of chapters, append the `--start` and/or `--end` options.

> **Note:** `--start` and `--end` are *inclusive*, i.e., using `--start 2 --end 3` will download chapters 2 and 3.

To convert an existing folder without downloading anything (like a stripped-down version of https://github.com/ciromattia/kcc), use the `convert` command.

```
mandown convert <FORMAT> <PATH_TO_FOLDER>
```

To process an existing folder without downloading anything, use the `process` command.

```
mandown process <PROCESS_OPERATIONS> <PATH_TO_FOLDER>
```

Where `PROCESS_OPERATIONS` is an option found from running `mandown process --help`.

Run `mandown --help` for more info.

## Basic library usage

See the [docs](/docs/) for more information and examples.

To just download the images:
```python
import mandown

mandown.download("https://comic-site.com/the-best-comic")
```

To download and convert to EPUB:
```python
import mandown

comic = mandown.query("https://comic-site.com/the-best-comic")
mandown.download(comic)
mandown.convert(comic, title=comic.metadata.title, to="epub")
```
