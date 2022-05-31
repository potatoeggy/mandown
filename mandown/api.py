# pylint: disable=invalid-name
import multiprocessing as mp
import os
from pathlib import Path
from typing import Iterable

from . import iohandler, processing, sources
from .processing import ProcessOps
from .sources.base_source import BaseSource, Chapter
from .sources.local_source import LocalSource


def query(url: str, populate: bool = True) -> BaseSource:
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
            pass
    return source


def download_chapter_progress(
    chapter: Chapter, dest_folder: str, maxthreads: int = 1, only_needed: bool = True
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

    download_folder = os.path.join(dest_folder, chapter.slug)
    if not os.path.isdir(download_folder):
        os.mkdir(download_folder)

    padding = len(str(len(chapter.images)))
    skip_images: set[int] = set()
    if only_needed:
        for f in os.listdir(download_folder):
            name = Path(f).stem
            if name == name.rjust(padding, "0"):
                try:
                    skip_images.add(int(name))
                except ValueError:
                    # expected if it's not an image
                    pass

    if len(skip_images) != len(chapter.images):
        # zip will crash if fed an empty array
        processed_chapter_images, filestems = zip(
            *(
                (link, str(i).rjust(padding, "0"))
                for i, link in enumerate(chapter.images, start=1)
                if i not in skip_images
            )
        )

        yield from iohandler.download(
            processed_chapter_images,
            os.path.join(dest_folder, download_folder),
            chapter.headers,
            maxthreads,
            filestems,
        )


def download_chapter(
    chapter: Chapter, dest_folder: str, maxthreads: int = 1, only_needed: bool = True
) -> None:
    """
    Download the images of a chapter to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    for _ in download_chapter_progress(chapter, dest_folder, maxthreads, only_needed):
        pass


def process_progress(
    folder_paths: list[Path], options: list[ProcessOps], maxthreads: int = 4
) -> Iterable[None]:
    map_pool: list[tuple[Path | str, list[ProcessOps]]] = []
    for folder in folder_paths:
        for image_path in folder.iterdir():
            if image_path.is_file():
                map_pool.append((image_path.absolute(), options))

    with mp.Pool(maxthreads) as pool:
        yield from pool.imap_unordered(processing.async_process, map_pool)


def process(
    folder_paths: list[Path], options: list[ProcessOps], maxthreads: int = 4
) -> None:
    for _ in process_progress(folder_paths, options, maxthreads):
        pass


def read_from(path: Path | str) -> LocalSource:
    return LocalSource(path)
