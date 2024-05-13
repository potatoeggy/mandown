from enum import Enum
from pathlib import Path
from typing import Iterator

import comicon


class ConvertFormats(str, Enum):
    """
    The formats that mandown can convert to. This is used for the `--format` option.
    """

    # for typing purposes
    CBZ = "cbz"
    EPUB = "epub"
    PDF = "pdf"
    MOBI = "mobi"
    NONE = "none"


def convert_one(
    comic: comicon.Comic, comic_path: Path, to: ConvertFormats, dest_folder: Path
) -> Iterator[str | int]:
    # save comicon.json
    (comic_path / comicon.cirtools.IR_DATA_FILE).write_text(comic.to_json())

    yield from comicon.outputs.create_comic_progress(
        comic_path, dest_folder / f"{comic.metadata.title_slug}.{to.value}"
    )
