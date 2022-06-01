import os
import zipfile
from pathlib import Path
from typing import Iterable

from .base_converter import ACCEPTED_IMAGE_EXTENSIONS, BaseConverter


class CbzConverter(BaseConverter):
    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[None]:
        path = Path(path)
        save_to = Path(save_to)

        dest_file = save_to / f"{self.comic.metadata.title}.cbz"

        with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as file:
            for dirpath, _, filenames in os.walk(path):
                yield "Compressing"
                for name in filenames:
                    if (Path(dirpath) / name).is_file():
                        file.write(
                            Path(dirpath) / name,
                            Path(dirpath.lstrip(str(path))) / name,
                            zipfile.ZIP_DEFLATED,
                        )


def get_class() -> CbzConverter:
    return CbzConverter
