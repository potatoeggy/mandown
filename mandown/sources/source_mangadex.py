"""
Source file for mangadex.org
"""
# pylint: disable=invalid-name

import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_source import BaseSource, Chapter, MangaMetadata


class MangaDexSource(BaseSource):
    name = "MangaDex"

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: Optional[BeautifulSoup] = None

        # https://api.mangadex.org/manga/de4b3c43-5243-4399-9fc3-68a3c0747138
        self.id = self.url.split("/")[4]
        if self.url.startswith("https://mangadex.org/chapter"):
            r: dict = self._get(f"https://api.mangadex.org/chapter/{self.id}").json()[
                "data"
            ]["relationships"]
            self.id: str = next(filter(lambda i: i["type"] == "manga", r))["id"]  # type: ignore

    def fetch_metadata(self) -> MangaMetadata:
        # TODO: support non-English downloads
        r = self._get(
            f"https://api.mangadex.org/manga/{self.id}?includes[]=author&includes[]=cover_art"
        ).json()

        metadata = r["data"]

        # use english if possible, otherwise use the first language that appears
        lang_code = (
            "en"
            if "en" in metadata["attributes"]["title"]
            else next(iter(metadata["attributes"]["title"]))
        )
        title: str = metadata["attributes"]["title"][lang_code]
        authors: list[str] = []
        for d in metadata["relationships"]:
            if d["type"] == "author":
                authors.append(d["attributes"]["name"])
            elif d["type"] == "cover_art":
                pass

        return MangaMetadata(title, authors, f"https://mangadex.org/title/{self.id}")

    def fetch_chapter_list(self) -> list[Chapter]:
        # for some reason *sometimes* it goes all name/service not found
        r: dict = self._get(f"https://api.mangadex.org/chapter?manga={self.id}").json()

        chapters: list[Chapter] = []
        for c in r["data"]:
            chapters.append(
                Chapter(
                    self,
                    c["attributes"]["title"],
                    f"https://mangadex.org/chapter/{c['id']}",
                )
            )
        return chapters

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        *_, chapter_id = chapter.url.split("/")
        r = self._get(f"https://api.mangadex.org/at-home/server/{chapter_id}").json()
        base_url = r["baseUrl"]
        chapter_hash = r["chapter"]["hash"]

        images: list[str] = []
        for p in r["chapter"]["data"]:
            images.append(f"{base_url}/data/{chapter_hash}/{p}")
        return images

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://mangadex.org/title/.*", url)
            or re.match(r"https://mangadex.org/chapter/.*", url)
        )

    @staticmethod
    def _get(url: str) -> requests.Response:
        """
        A wrapper of requests.get for MangaDex with
        rudimentary rate-limit processing
        """
        while (r := requests.get(url)).status_code != 200:
            time.sleep(1)
        return r


def get_class() -> type[BaseSource]:
    return MangaDexSource
