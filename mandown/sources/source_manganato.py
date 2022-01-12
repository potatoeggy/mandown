"""
Source file for readmanganato.com
"""
# pylint: disable=invalid-name

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_source import BaseSource, Chapter, MangaMetadata


class MangaNatoSource(BaseSource):
    name = "MangaNato"
    headers = {"Referer": "https://readmanganato.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self._scripts: Optional[str] = None

    def fetch_metadata(self) -> MangaMetadata:
        soup = BeautifulSoup(self._get_scripts(), "html.parser")
        title: str = soup.h1.next_element
        authors_genres = soup.select("td > a.a-h")
        authors: list[str] = []
        genres: list[str] = []
        for el in authors_genres:
            if el["href"].startswith("https://manganato.com/author"):
                authors.append(el.next_element)
            elif el["href"].startswith("https://manganato.com/genre"):
                genres.append(el.next_element)

        return MangaMetadata(title, authors, self.url)

    def fetch_chapter_list(self) -> list[Chapter]:
        soup = BeautifulSoup(self._get_scripts(), "html.parser")
        chapters = list(
            map(
                lambda c: Chapter(self, c.next_element, c["href"], self.headers),
                soup.select("a.chapter-name"),
            )
        )
        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "html.parser")
        images = []
        for i in soup.find_all("img"):
            if not i["src"].startswith("https://readmanganato.com"):
                images.append(i["src"])
        return images

    def _get_scripts(self) -> str:
        if self._scripts:
            return self._scripts

        self._scripts = requests.get(self.url).text
        return self._scripts

    @classmethod
    def url_to_id(cls, url: str) -> str:
        *_, last_item = filter(None, url.split("/"))
        return last_item

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://readmanganato.com/.*", url))


def get_class() -> type[BaseSource]:
    return MangaNatoSource
