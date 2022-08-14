# mandown

![Supported Python versions](https://img.shields.io/pypi/pyversions/mandown)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Download from PyPI](https://img.shields.io/pypi/v/mandown)](https://pypi.org/project/mandown)
[![Download from the AUR](https://img.shields.io/aur/version/mandown-git)](https://aur.archlinux.org/packages/mandown-git)
[![Latest release](https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag)](https://github.com/potatoeggy/mandown/releases/latest)
[![License](https://img.shields.io/github/license/potatoeggy/mandown)](/LICENSE)

Comic downloader and converter to CBZ, EPUB, and/or PDF as a Python library and command line application.

## Supported sites

To request a new site, please file a [new issue](https://github.com/potatoeggy/mandown/issues/new).

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

Arch Linux users may also install the package from the [AUR](https://aur.archlinux.org/packages/mandown.git):

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

## Usage

```
mandown get <URL>
```

To convert the download contents to CBZ/EPUB, append the `--convert` option. To apply image processing to the downloaded images, append the `--process` option.

```
mandown get <URL> --convert epub --process rotate_double_pages
```

To convert an existing folder without downloading anything except metadata (like a stripped-down version of https://github.com/ciromattia/kcc), use the `convert` command.

```
mandown convert <FORMAT> <PATH_TO_FOLDER>
```

Run `mandown --help` for more info.

## Library usage

```python
import mandown

# load a previously downloaded comic...
comic = mandown.load("path/to/comic/folder")
print(comic.metadata, comic.chapters)

# ...OR fetch a comic from a source by URL
comic = mandown.query(url_to_comic)
print(comic.metadata, comic.chapters)

# download comic to ./comic using 4 threads
mandown.download(comic, "./comic/", threads=4)

# apply image post-processing to comic images in ./comic
mandown.process("./comic/", options=["rotate_double_pages", "trim_borders"])

# convert comic located in ./comic to epub, storing it in ./epubs
mandown.convert(comic, "./comic/", "epub", "./epubs")
```
