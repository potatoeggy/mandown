"""
Converts a folder of images to EPUB/PDF/CBZ/CBR/MOBI
"""
import os
import shutil
from typing import Optional

from mandown.sources.base_source import MangaMetadata, Chapter


class Converter:
    def __init__(
        self,
        folder_path: str,
        dest: str = os.getcwd(),
        metadata: Optional[MangaMetadata] = None,
        chapter_list: Optional[list[Chapter]] = None,
    ) -> None:
        if not os.path.isdir(folder_path):
            raise ValueError(f"{folder_path} is not a directory.")

        self.folder_path = os.path.realpath(folder_path)
        self.metadata = metadata or MangaMetadata(
            title=os.path.basename(self.folder_path), authors=[], url=""
        )

        # self.chapters is found either by traversing the path (natsort) or by being fed

    def to_cbr(self) -> None:
        pass

    def to_cbz(self) -> None:
        pass

    def to_epub(self) -> None:
        pass

    def to_pdf(self):
        pass

    def to_mobi(self):
        pass
