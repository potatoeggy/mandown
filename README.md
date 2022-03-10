# mandown

<a href="https://www.codefactor.io/repository/github/potatoeggy/mandown"><img src="https://www.codefactor.io/repository/github/potatoeggy/mandown/badge" alt="CodeFactor" /></a>
<a href="https://pypi.org/project/mandown"><img src="https://img.shields.io/pypi/v/mandown" /></a>
<a href="https://aur.archlinux.org/packages/mandown-git"><img src="https://img.shields.io/aur/version/mandown-git" /></a>
<a href="https://github.com/potatoeggy/mandown/releases/latest"><img src="https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag" /></a>
<a href="/LICENSE"><img src="https://img.shields.io/github/license/potatoeggy/mandown" /></a>

Comic downloader and converter to CBZ and EPUB as a Python library and command line application.

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
mandown download <URL>
```

To convert the download contents to CBZ/EPUB, append the `--convert` option. To apply image processing to the downloaded images, append the `--process` option.

```
mandown download <URL> --convert epub --process rotate_double_pages
```

To convert an existing folder without downloading anything except metadata (like a stripped-down version of https://github.com/ciromattia/kcc), use the `convert` command.

```
mandown convert <FORMAT> <PATH_TO_FOLDER>
```

Run `mandown --help` for more info.

## Library usage

```python
import os
import mandown

manga = mandown.query(url_to_manga)
print(manga.metadata, manga.chapters)
for c in manga.chapters:
    mandown.download_chapter(c, dest_folder=os.getcwd(), maxthreads=4)
```
