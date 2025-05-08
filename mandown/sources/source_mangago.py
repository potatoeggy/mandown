"""
Source file for mangago.me
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class MangagoSource(CommonSource):
    name = "Mangago"
    domains = ["https://mangago.me"]

    def __init__(self, url: str) -> None:
        # https://www.mangago.me/read-manga/unordinary/
        # we want "unordinary"
        self.id = url.split("/")[4]
        url = f"https://www.mangago.me/read-manga/{self.id}"
        super().__init__(url)

    def _fetch_metadata(self) -> BaseMetadata:
        page = self._get_soup()
        title = page.select_one(".w-title > h1").text.strip()

        potential_author_els = page.select(".manga_right td a:not(.chico)")
        authors: list[str] = [
            s.text.strip() for s in potential_author_els if "l_search" in s["href"]
        ]

        genres_els = page.select("td[style] > a")
        genres = [s.text.strip() for s in genres_els if "genre" in s["href"]]

        description: str = page.select_one(".manga_summary").text.strip()
        cover_art: str = page.select_one(".left.cover img")["src"]

        return BaseMetadata(
            title,
            authors,
            self.url,
            genres,
            description,
            cover_art,
        )

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = self._get_soup()
        chapters = [BaseChapter(c.text, c["href"]) for c in soup.select("#chapter_table tr h4 > a")]

        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        body = requests.get(chapter.url).text
        soup = BeautifulSoup(body, "lxml")
        print(body)

        # find the number in "total_pages=26,"
        total_pages_start = body.index("total_pages=") + len("total_pages=")
        total_pages_end = body.index(",", total_pages_start)
        num_pages = int(body[total_pages_start:total_pages_end])

        images: list[str] = [soup.select_one("img#page1")["src"]]
        for i in range(2, num_pages + 1):
            link = f"{chapter.url}/{i}/"
            soup = BeautifulSoup(requests.get(link).text, "lxml")
            images.append(soup.select_one(f"img#page{i}")["src"])
        return images

    def _get_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self._get_scripts(), "lxml")

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://www.mangago.me/read-manga/.*", url))


def get_class() -> type[CommonSource]:
    return MangagoSource
