"""
Source file for webtoons.com
"""
# pylint: disable=invalid-name

import re

import feedparser
import requests
from bs4 import BeautifulSoup

from ..comic import BaseChapter, BaseMetadata
from .base_source import BaseSource


class WebtoonsSource(BaseSource):
    name = "Webtoons"
    domains = ["https://webtoons.com"]
    headers = {"Referer": "https://webtoons.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: BeautifulSoup | None = None

        title_no_index = url.index("?title_no=") + len("?title_no=")
        title_no_end_index: int | None = url.find("&", title_no_index)
        if title_no_end_index == -1:
            title_no_end_index = None

        self._title_no = int(url[title_no_index:title_no_end_index])

        self._title_path = "/".join(url.split("/")[3:6])

    def fetch_metadata(self) -> BaseMetadata:
        feed = feedparser.parse(
            f"https://www.webtoons.com/{self._title_path}/rss?title_no={self._title_no}"
        )
        feed = feedparser.parse(
            f"https://www.webtoons.com/{self._title_path}/rss?title_no={self._title_no}"
        )
        authors: list[str] = feed["entries"][0].author.split("/")
        authors = [s.strip() for s in authors]
        title: str = feed["channel"]["title"]
        cover_art: str = feed["channel"]["image"]["href"]
        description: str = feed["channel"]["description"].strip()

        return BaseMetadata(
            title,
            authors,
            f"https://www.webtoons.com/{self._title_path}/list?title_no={self._title_no}",
            ["Webtoons.com does not support genres"],
            description,
            cover_art,
        )

    def fetch_chapter_list(self) -> list[BaseChapter]:
        soup = self._get_soup()
        titles = [
            str(e.next_element) for e in soup.select("p.sub_title > span.ellipsis")
        ]

        links: list[str] = [e["href"] for e in soup.select('a[class^="NPI=a:list"]')]

        chapters = [BaseChapter(self, t, u) for t, u in zip(titles, links)]
        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "html.parser")
        images: list[str] = []
        for c in soup.select("div#_imageList > img"):
            images.append(c["data-url"])
        return images

    def _get_soup(self) -> BeautifulSoup:
        if self._soup:
            return self._soup

        # mobile serves all chapters in one page
        mobile_url = (
            f"https://m.webtoons.com/{self._title_path}/list?title_no={self._title_no}"
        )

        self._soup = BeautifulSoup(
            requests.get(mobile_url, headers=self.headers).text,
            "html.parser",
        )
        return self._soup

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://www.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://m.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://www.webtoons.com/.*/viewer\?title_no=.*", url)
        )


def get_class() -> type[BaseSource]:
    return WebtoonsSource
