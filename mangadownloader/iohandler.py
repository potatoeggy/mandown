from pathlib import Path
import requests
import os

from mangadownloader.sources.base_source import Chapter


class IOHandler:
    def __init__(self):
        pass

    def download(self, urls: list[str] | str, dest_folder: str) -> None:
        if isinstance(urls, str):
            urls = [urls]

        if not os.path.exists(dest_folder):
            raise ValueError(f"Path {dest_folder} does not exist")

        for url in urls:
            name = url.split("/")[-1]
            dest_file = os.path.join(dest_folder, name)

            print(f"Saving {url} to {dest_file}")
            r = requests.get(url, stream=True)
            with open(dest_file, "wb") as file:
                for ch in r:
                    file.write(ch)

    def download_chapter(self, chapter: Chapter, dest_folder: str) -> None:
        self.download(chapter.images, dest_folder)
