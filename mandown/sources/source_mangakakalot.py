"""
Source file for mangakakalot.com
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class MangaNatoSource(CommonSource):
    name = "MangaKakalot"
    domains = ["https://mangakakalot.com"]
    headers = {"Referer": "https://mangakakalot.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")
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

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(self._get_scripts(), "lxml")
        chapters = [BaseChapter(c.next_element, c["href"]) for c in soup.select(".row > span > a")]
        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        images = []
        for i in soup.select(".container-chapter-reader > img"):
            images.append(i["src"])
        return images

    @classmethod
    def url_to_id(cls, url: str) -> str:
        *_, last_item = filter(None, url.split("/"))
        return last_item

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://mangakakalot.com/manga/.*", url))


def get_class() -> type[CommonSource]:
    return MangaNatoSource
