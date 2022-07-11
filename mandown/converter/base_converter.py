from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Literal

from ..comic import BaseComic

ACCEPTED_IMAGE_EXTENSIONS = {
    ".gif": "gif",
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".jpe": "jpeg",
}


class ConvertFormats(str, Enum):
    # for typing purposes
    CBZ = "cbz"
    EPUB = "epub"
    PDF = "pdf"
    NONE = "none"


@dataclass(kw_only=True)
class ConvertOptions:
    page_progression: Literal["rtl"] | Literal["ltr"] = "ltr"


class BaseConverter:
    def __init__(self, comic: BaseComic, options: ConvertOptions | None = None) -> None:
        self.comic = comic
        self.options = options or ConvertOptions()

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[str]:
        raise NotImplementedError

    def create_file(self, path: Path | str, save_to: Path | str) -> None:
        for _ in self.create_file_progress(path, save_to):
            pass
