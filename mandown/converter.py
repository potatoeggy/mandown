"""
Converts a folder of images to EPUB/PDF/CBZ/CBR/MOBI
"""
import os
from pathlib import Path
import shutil
from typing import Optional

from natsort import natsorted

from mandown.sources.base_source import MangaMetadata


class Converter:
    ACCEPTED_IMAGE_EXTENSIONS = ["gif", "png", ".jpg", ".jpeg", ".jpe"]

    def __init__(
        self,
        folder_path: str,
        metadata: Optional[MangaMetadata] = None,
        chapter_list: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        """
        Get the file path of a comic and identify its metadata.
        The chapter list is a list of tuples in the format
        (`chapter_path`, `chapter_title`), where `chapter_path`
        is the path of the chapter relative to `folder_path`.

        If the chapter list or metadata are not provided, they will
        be guessed from the directory structure.
        """
        if not Path(folder_path).is_dir():
            raise ValueError(f"{folder_path} is not a directory.")

        self.folder_path = os.path.realpath(folder_path)
        self.metadata = metadata or MangaMetadata(
            title=os.path.basename(self.folder_path), authors=[], url=""
        )

        # self.chapters is found either by traversing the path (natsort) or by being fed
        self.chapters = chapter_list
        if self.chapters is None:
            self.chapters = []
            for item in natsorted(os.listdir(self.folder_path)):
                item = str(item)  # get rid of type complaints
                if (Path(self.folder_path) / item).is_dir():
                    self.chapters.append((item, item))

        if sorted(self.chapters) != self.chapters:
            padding = f"0{len(str(len(self.chapters)))}"
            self.chapters = [
                (f"{i:{padding}}. {c[0]}", c[1]) for i, c in enumerate(self.chapters)
            ]

    def to_cbr(self) -> None:
        pass

    def to_cbz(self) -> None:
        zip_path = shutil.make_archive(
            self.metadata.title,
            "zip",
            self.folder_path,
        )

        cbz_path = Path(zip_path).stem + ".cbz"
        os.rename(zip_path, cbz_path)

    def to_epub(self) -> None:
        pass

    def to_pdf(self) -> None:
        pass

    def to_mobi(self) -> None:
        pass


if __name__ == "__main__":
    comic = Converter("/media/cbz/RAW_Oshi no Ko")
    comic.to_cbz()
