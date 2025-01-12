"""
Source file for comixextra.com
"""

import re

from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from ..request_utils import requests
from .common_source import CommonSource


class ComixExtraSource(CommonSource):
    name = "Comix Extra"
    domains = ["https://comixextra.com"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)  # we make a GET request here which is not ideal
        self.url = f"https://comixextra.com/comic/{self.id}"
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        title: str = soup.select_one(".mobile-hide span.title-1").text.strip()

        authors: list[str] = []
        genres: list[str] = []
        for item in soup.select_one("dl.movie-dl").children:
            if item.name == "dt":
                if item.text == "Author:":
                    authors = item.find_next_sibling("dd").text.strip().split(",")
                elif item.text == "Genres:":
                    genres = [g.text.strip() for g in item.find_next_sibling("dd").select("a")]

        cover_art: str = soup.select_one(".movie-image img")["src"]

        description = soup.select_one("#film-content").text.strip()

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        return list(
            reversed(
                [
                    BaseChapter(c.text, f"{c['href']}/full")
                    for c in soup.select(".episode-list #list a")
                ]
            )
        )

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        text = requests.get(chapter.url).text

        return [i["src"] for i in BeautifulSoup(text, "lxml").select(".chapter-container img")]

    @classmethod
    def url_to_id(cls, url: str) -> str:
        items = list(filter(None, url.split("/")))

        # e.g., for https://comixextra.com/comic/nottingham and
        # https://comixextra.com/nottingham/issue-12
        # we want 'nottingham'

        if "comic" in items:
            return items[items.index("comic") + 1]
        return items[items.index("comixextra.com") + 1]

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://comixextra.com/.*", url))


def get_class() -> type[CommonSource]:
    return ComixExtraSource
