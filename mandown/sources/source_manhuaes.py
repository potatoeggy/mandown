"""
Source file for manhuaes.com
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class ManhuaESSource(CommonSource):
    name = "ManhuaAZ"
    domains = ["https://manhuaaz.com"]
    # headers = {"Referer": "https://mangakakalot.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self.url = f"https://manhuaaz.com/manga/{self.id}"
        self.numerical_id: str | None = None
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")
        self.numerical_id = soup.select_one("input.rating-post-id")["value"]

        title: str = soup.select_one(".manga-title-badges + h1").text.strip()
        authors: list[str] = [
            string.strip()
            for string in soup.select_one(".author-content").text.split(", ")
            if string.strip() != "Updating"
        ]
        genres: list[str] = [
            string.strip()
            for string in soup.select_one(".genres-content").text.split(", ")
            if string.strip() != "Updating"
        ]
        cover_art: str = soup.select_one(".summary_image img")["data-src"]
        description: str = soup.select_one(".summary__content").text.strip()

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        if not self.numerical_id:
            soup = BeautifulSoup(self._get_scripts(), "lxml")
            self.numerical_id = soup.select_one("input.rating-post-id")["value"]

        soup = BeautifulSoup(
            requests.post(
                "https://manhuaaz.com/wp-admin/admin-ajax.php",
                data={"action": "manga_get_chapters", "manga": self.numerical_id},
            ).text,
            "lxml",
        )
        chapters = [
            BaseChapter(c.text.strip(), c["href"]) for c in soup.select(".wp-manga-chapter a")
        ]
        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        return [el["data-src"] for el in soup.select("img.wp-manga-chapter-img")]

    @classmethod
    def url_to_id(cls, url: str) -> str:
        items = list(filter(None, url.split("/")))
        # e.g., for https://manhuaes.com/manga/the-undefeatable-swordsman-all/chapter-166/"
        # we want 'the-undefeatable-swordsman-all'
        return items[3]

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://manhua(es|az).com/manga/.*", url))


def get_class() -> type[CommonSource]:
    return ManhuaESSource
