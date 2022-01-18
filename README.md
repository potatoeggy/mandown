# mandown

<a href="https://pypi.org/project/mandown"><img src="https://img.shields.io/pypi/v/mandown" /></a>
<a href="https://github.com/potatoeggy/mandown/releases/latest"><img src="https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag" /></a>
<a href="/LICENSE"><img src="https://img.shields.io/github/license/potatoeggy/mandown" /></a>

Python library and command line application to download comics from various sources

## Supported sites

- https://mangasee123.com
- https://manganato.com
- https://webtoons.com
- https://mangadex.org

## Installation

Install the package from PyPI:

```
pip3 install mandown
```

Or, to build from source:

```
git clone https://github.com/potatoeggy/mandown.git
poetry install
poetry build
pip3 install dist/mandown*.whl
```

## Usage

```
mandown <URL>
```

Run `mandown --help` for more info.

## Library usage

```python
import os
from mandown import mandown

manga = mandown.query(url_to_manga)
print(manga.metadata, manga.chapters)
for c in manga.chapters:
    mandown.download_chapter(c, dest_folder=os.getcwd(), maxthreads=4)
```
