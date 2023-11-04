"""
Source file for blogtruyenmoi.com
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .base_source import BaseSource


class BlogTruyenMoiSource(BaseSource):
    name = "Blog Truyen"
    domains = ["https://blogtruyenmoi.com"]
    headers = {"Referer": "https://blogtruyenmoi.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)  # we make a GET request here which is not ideal
        self.url = f"https://blogtruyenmoi.com/{self.id}"
        self._scripts: str | None = None

    def fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        title: str = (
            soup.select_one("div#breadcrumbs > span:nth-child(2)")
            .text.split(" > ")[-1]
            .strip()
        )
        authors: list[str] = [
            soup.select_one("div.description > p:nth-child(1) > span").text
        ]
        genres: list[str] = [
            string.text.strip() for string in soup.select("span.category > a")
        ]
        cover_art: str = soup.select_one(".thumbnail > img")["src"]

        description_list: list[str] = []
        for para in soup.select("div.detail > div.content > div.content > p"):
            stripped = para.text.strip()
            if not stripped:
                break
            description_list.append(stripped)
        description = "\n".join(description_list)

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        chapters = [
            BaseChapter(c.text.strip(), f"https://blogtruyenmoi.com/{c['href']}")
            for c in soup.select("div#list-chapters > p > span > a")
        ]
        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        return [el["src"] for el in soup.select("article#content > img")]

    def _get_scripts(self) -> str:
        if self._scripts:
            return self._scripts

        self._scripts = requests.get(self.url).text or ""
        return self._scripts

    @classmethod
    def url_to_id(cls, url: str) -> str:
        items = list(filter(None, url.split("/")))
        # e.g., for https://blogtruyenmoi.com/31844/doc-la-dungeon
        # we want '31844'
        # for https://blogtruyenmoi.com/c842985/doc-la-dungeon-chap-62
        # we want to crawl the page and find the link back to the ID

        try:
            return int(items[2])
        except ValueError:
            soup = BeautifulSoup(requests.get(url).text, "lxml")
            return (
                soup.select_one("header div.breadcrumbs > a:not([href='/'])")
                .attrs["href"]
                .split("/")[1]
            )

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://blogtruyenmoi.com/(\d*(/.*)?)|(c.\d*/.*)", url))


def get_class() -> type[BaseSource]:
    return BlogTruyenMoiSource
