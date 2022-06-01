from pathlib import Path
from typing import Iterable

from ..comic import Comic
from . import ConvertOptions

ACCEPTED_IMAGE_EXTENSIONS = {
    ".gif": "gif",
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".jpe": "jpeg",
}


class BaseConverter:
    def __init__(self, comic: Comic, options: ConvertOptions | None = None) -> None:
        self.comic = comic
        self.options = options or ConvertOptions()

    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[None]:
        raise NotImplementedError

    def create_file(self, path: Path | str, save_to: Path | str) -> None:
        for _ in self.create_file_progress(path, save_to):
            pass
