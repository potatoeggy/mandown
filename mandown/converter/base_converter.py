from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator, Literal

from ..comic import BaseComic

ACCEPTED_IMAGE_EXTENSIONS = {
    ".gif": "gif",
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".jpe": "jpeg",
}


class ConvertFormats(str, Enum):
    """
    The formats that mandown can convert to. This is used for the `--format` option.
    """

    # for typing purposes
    CBZ = "cbz"
    EPUB = "epub"
    PDF = "pdf"
    NONE = "none"


@dataclass(kw_only=True, slots=True)
class ConvertOptions:
    """
    Options for converters.

    :param `page_progression`: The page progression of the comic. This is used for EPUBs.
    """

    page_progression: Literal["rtl"] | Literal["ltr"] = "ltr"


class BaseConverter:
    """
    Base class for converters.

    :param `comic`: A comic with metadata to convert
    :param `options`: Options for the converter
    """

    def __init__(self, comic: BaseComic, options: ConvertOptions | None = None) -> None:
        self.comic = comic
        self.options = options or ConvertOptions()

        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Post-initialization hook. This is called after the constructor has finished, and is useful for setting up the converter.
        """

    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterator[str]:
        """
        Convert the comic in `path` and save it to `save_to`.

        :param `path`: A folder containing the comic to convert
        :param `save_to`: A folder to put the converted comic in

        :returns An `Iterator` representing a progress bar up to the number of chapters in the comic.

        :raises `NotImplementedError`: If the converter is not supported yet.
        """
        raise NotImplementedError

    def create_file(self, path: Path | str, save_to: Path | str) -> None:
        """
        Convert the comic in `path` and save it to `save_to`.

        :param `path`: A folder containing the comic to convert
        :param `save_to`: A folder to put the converted comic in

        :raises `NotImplementedError`: If the converter is not supported yet.
        """
        for _ in self.create_file_progress(path, save_to):
            pass
