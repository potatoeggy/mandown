"""
Source file for blogtruyenmoi.com
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class BlogTruyenMoiSource(CommonSource):
    name = "Blog Truyen"
    domains = ["https://blogtruyenmoi.com"]
    headers = {"Referer": "https://blogtruyenmoi.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)  # we make a GET request here which is not ideal
        self.url = f"https://blogtruyenmoi.com/{self.id}"
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        title: str = (
            soup.select_one("div#breadcrumbs > span:nth-child(2)").text.split(" > ")[-1].strip()
        )
        authors: list[str] = [soup.select_one('div.description > p > a[href^="/tac-gia"]').text]
        genres: list[str] = [string.text.strip() for string in soup.select("span.category > a")]
        cover_art: str = soup.select_one(".thumbnail > img")["src"]

        description_list: list[str] = []
        for child in soup.select_one("div.detail > div.content").children:
            if child.name and child.name.lower() == "br":
                # br tags usually indicate the end of the description
                break

            stripped = child.text.strip()
            if not stripped:
                break
            description_list.append(stripped)
        description = "\n".join(description_list)

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        chapters = [
            BaseChapter(c.text.strip(), f"https://blogtruyenmoi.com/{c['href']}")
            for c in soup.select("div#list-chapters > p > span > a")
        ]
        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        return [el["src"] for el in soup.select("article#content > img")]

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


def get_class() -> type[CommonSource]:
    return BlogTruyenMoiSource
