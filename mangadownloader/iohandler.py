"""
Handles source management and identification
"""
import os
import requests

from mangadownloader.sources.base_source import Chapter


def download(urls: list[str] | str, dest_folder: str) -> None:
    """
    Download one or multiple URLs to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    if isinstance(urls, str):
        urls = [urls]

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    print(f"    {len(urls)} links found.")
    for i, url in enumerate(urls):
        name = url.split("/")[-1]
        dest_file = os.path.join(dest_folder, name)

        print(f"    ({i+1}/{len(urls)}) DL {url} -> {dest_file}")
        response = requests.get(url, stream=True)
        with open(dest_file, "wb") as file:
            for char in response:
                file.write(char)


def download_chapter(chapter: Chapter, dest_folder: str) -> None:
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

    download(chapter.images, os.path.join(dest_folder, chapter.title))
