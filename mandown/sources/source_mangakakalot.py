"""
Source file for mangakakalot.com
"""
# pylint: disable=invalid-name

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base_source import BaseSource, Chapter, MangaMetadata


class MangaNatoSource(BaseSource):
    name = "MangaKakalot"
    domains = ["https://mangakakalot.com"]
    headers = {"Referer": "https://mangakakalot.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self._scripts: Optional[str] = None

    def fetch_metadata(self) -> MangaMetadata:
        soup = BeautifulSoup(self._get_scripts(), "html.parser")
        title: str = soup.h1.next_element
        authors_genres = soup.select(".manga-info-text > li > a")
        authors: list[str] = []
        genres: list[str] = []
        for el in authors_genres:
            if el["href"].startswith("https://mangakakalot.com/search/author"):
                authors.append(el.next_element)
            elif el["href"].startswith("https://mangakakalot.com/manga_list"):
                genres.append(el.next_element)

        cover_img = next(iter(soup.select(".manga-info-pic > img")))
        cover_art: str = cover_img["src"]

        description_html = soup.select_one("#noidungm")
        description_html.find("p").replace_with("")  # remove p block
        description = description_html.get_text().strip()

        return MangaMetadata(title, authors, self.url, genres, description, cover_art)

    def fetch_chapter_list(self) -> list[Chapter]:
        soup = BeautifulSoup(self._get_scripts(), "html.parser")
        chapters = list(
            map(
                lambda c: Chapter(self, c.next_element, c["href"], self.headers),
                soup.select(".row > span > a"),
            )
        )
        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text)
        images = []
        for i in soup.select(".container-chapter-reader > img"):
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
        return bool(re.match(r"https://mangakakalot.com/manga/.*", url))


def get_class() -> type[BaseSource]:
    return MangaNatoSource
