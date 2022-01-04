import os
from pathlib import Path
import requests

from mangadownloader.sources.base_source import Chapter


def download(urls: list[str] | str, dest_folder: str) -> None:
    if isinstance(urls, str):
        urls = [urls]

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    for url in urls:
        name = url.split("/")[-1]
        dest_file = os.path.join(dest_folder, name)

        response = requests.get(url, stream=True)
        with open(dest_file, "wb") as file:
            for char in response:
                file.write(char)


def download_chapter(chapter: Chapter, dest_folder: str) -> None:
    download(chapter.images, os.path.join(dest_folder, chapter.title))
