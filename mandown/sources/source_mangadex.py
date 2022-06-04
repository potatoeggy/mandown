"""
Source file for mangadex.org
"""
# pylint: disable=invalid-name

import re
import time

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .base_source import BaseSource


class MangaDexSource(BaseSource):
    name = "MangaDex"
    domains = ["https://mangadex.org"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: BeautifulSoup | None = None
        self.lang_code = ""

        # https://api.mangadex.org/manga/de4b3c43-5243-4399-9fc3-68a3c0747138
        self.id = self.url.split("/")[4]
        if self.url.startswith("https://mangadex.org/chapter"):
            r: dict = self._get(f"https://api.mangadex.org/chapter/{self.id}").json()[
                "data"
            ]["relationships"]
            self.id: str = next(filter(lambda i: i["type"] == "manga", r))["id"]  # type: ignore

    def fetch_metadata(self) -> BaseMetadata:
        # TODO: support non-English downloads
        r = self._get(
            f"https://api.mangadex.org/manga/{self.id}"
            "?includes[]=author&includes[]=cover_art&includes[]=artist"
        ).json()

        metadata: dict = r["data"]

        # use english if possible, otherwise use the first language that appears
        self.lang_code = (
            "en"
            if "en" in metadata["attributes"]["title"]
            else next(iter(metadata["attributes"]["title"]))
        )
        title: str = metadata["attributes"]["title"][self.lang_code]
        description: str = metadata["attributes"]["description"][self.lang_code]

        authors: list[str] = []
        cover_art = ""
        for d in metadata["relationships"]:
            if d["type"] == "author" or d["type"] == "artist":
                authors.append(d["attributes"]["name"])
            elif d["type"] == "cover_art":
                # pylint: disable=line-too-long
                cover_art = (
                    "https://uploads.mangadex.org/covers/"
                    f"{self.id}/{d['attributes']['fileName']}"
                )

        genres: list[str] = []
        for d in metadata["attributes"]["tags"]:
            if d["attributes"]["group"] == "genre":
                genres.append(d["attributes"]["name"][self.lang_code])

        return BaseMetadata(
            title,
            authors,
            f"https://mangadex.org/title/{self.id}",
            genres,
            description,
            cover_art,
        )

    def fetch_chapter_list(self) -> list[BaseChapter]:
        # for some reason *sometimes* it goes all name/service not found
        r = self._get(
            f"https://api.mangadex.org/manga/{self.id}/"
            f"feed?limit=500&translatedLanguage[]={self.lang_code}"
            "&order[volume]=desc&order[chapter]=desc"
        ).json()

        chapters: list[BaseChapter] = []
        for c in r["data"]:
            chapters.append(
                BaseChapter(
                    c["attributes"]["title"] or f"Chapter {c['attributes']['chapter']}",
                    f"https://mangadex.org/chapter/{c['id']}",
                )
            )
        return chapters

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
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
