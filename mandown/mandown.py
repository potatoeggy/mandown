import os

from mandown import iohandler, sources
from mandown.sources.base_source import BaseSource, Chapter


def query(url: str) -> BaseSource:
    """
    Return the source file for a URL.
    """
    return sources.get_class_for(url)(url)


def download_chapter(chapter: Chapter, dest_folder: str, maxthreads: int = 1) -> None:
    """
    Download the images of a chapter to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    if not chapter.images:
        raise ValueError("No images available to download")

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    download_folder = os.path.join(dest_folder, chapter.title)
    if os.path.isdir(download_folder):
        print("WARN: chapter folder already exists, proceeding anyway")
    else:
        os.mkdir(download_folder)

    iohandler.download(
        chapter.images, os.path.join(dest_folder, chapter.title), maxthreads
    )
