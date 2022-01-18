"""
Source file for webtoons.com
"""
# pylint: disable=invalid-name

import re
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from .base_source import BaseSource, Chapter, MangaMetadata


class WebtoonsSource(BaseSource):
    name = "Webtoons"
    headers = {"Referer": "https://webtoons.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: Optional[BeautifulSoup] = None

        title_no_index = url.index("?title_no=") + len("?title_no=")
        title_no_end_index: Optional[int] = url.find("&", title_no_index)
        if title_no_end_index == -1:
            title_no_end_index = None

        self._title_no: int = int(url[title_no_index:title_no_end_index])

        self._title_path: str = "/".join(url.split("/")[3:6])

    def fetch_metadata(self) -> MangaMetadata:
        feed = feedparser.parse(
            f"https://www.webtoons.com/{self._title_path}/rss?title_no={self._title_no}"
        )
        feed = feedparser.parse(
            f"https://www.webtoons.com/{self._title_path}/rss?title_no={self._title_no}"
        )
        authors: list[str] = feed["entries"][0].author.split("/")
        authors = list(map(lambda s: s.strip(), authors))
        title: str = feed["channel"]["title"]

        return MangaMetadata(
            title,
            authors,
            f"https://www.webtoons.com/{self._title_path}/list?title_no={self._title_no}",
        )

    def fetch_chapter_list(self) -> list[Chapter]:
        soup = self._get_soup()
        titles: list[str] = [
            str(e.next_element) for e in soup.select("p.sub_title > span.ellipsis")
        ]

        links: list[str] = [e["href"] for e in soup.select('a[class^="NPI=a:list"]')]

        chapters = [
            Chapter(self, t, u, {"Referer": "https://webtoons.com"})
            for t, u in zip(titles, links)
        ]
        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
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
            requests.get(
                mobile_url, headers={"Referer": "https://m.webtoons.com"}
            ).text,
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
