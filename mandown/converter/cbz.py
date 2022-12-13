import zipfile
from pathlib import Path
from typing import Iterator

from .base_converter import BaseConverter


class CbzConverter(BaseConverter):
    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterator[str]:
        path = Path(path).absolute()
        save_to = Path(save_to)

        dest_file = save_to / f"{self.comic.metadata.title}.cbz"

        with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as file:
            for outerpath in path.iterdir():
                if outerpath.is_dir():
                    for image in outerpath.iterdir():
                        yield "Compressing"
                        file.write(
                            image,
                            image.absolute().relative_to(path),
                            zipfile.ZIP_DEFLATED,
                        )
                elif outerpath.stem == "cover":
                    file.write(
                        outerpath,
                        # rename cover to appear first in the archive
                        outerpath.with_stem("__cover").absolute().relative_to(path),
                        zipfile.ZIP_DEFLATED,
                    )


def get_class() -> type[CbzConverter]:
    return CbzConverter
