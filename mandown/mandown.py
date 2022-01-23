# pylint: disable=invalid-name
import os
from typing import Iterable

from natsort import natsorted

from mandown import iohandler, sources
from mandown.sources.base_source import BaseSource, Chapter


def query(url: str, populate: bool = True, populate_sort: bool = True) -> BaseSource:
    """
    Return the source file for a URL.
    """
    source = sources.get_class_for(url)(url)
    if populate:
        # these statements are to trigger their getters to
        # fetch the data
        if source.metadata:
            pass
        if source.chapters:
            if populate_sort:
                titles = list(map(lambda c: c.title, source.chapters))
                if titles != natsorted(titles):
                    padding = f"0{len(str(len(source.chapters)))}"
                    for i, c in enumerate(source.chapters):
                        c.title = f"{i+1:{padding}}. {c.title}"
    return source


def download_chapter_progress(
    chapter: Chapter, dest_folder: str, maxthreads: int = 1
) -> Iterable[None]:
    """
    Download the images of a chapter to a destination folder.
    Returns a generator that increments whenever an item has finished
    downloading.
    Raises ValueError if the folder does not exist.
    """
    if not chapter.images:
        raise ValueError("No images available to download")

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    download_folder = os.path.join(dest_folder, chapter.title)
    if not os.path.isdir(download_folder):
        os.mkdir(download_folder)

    yield from iohandler.download(
        chapter.images,
        os.path.join(dest_folder, chapter.title_sanitised),
        chapter.headers,
        maxthreads,
    )


def download_chapter(chapter: Chapter, dest_folder: str, maxthreads: int = 1) -> None:
    """
    Download the images of a chapter to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    for _ in download_chapter_progress(chapter, dest_folder, maxthreads):
        pass
