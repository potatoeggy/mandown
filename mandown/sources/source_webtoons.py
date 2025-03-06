"""
Source file for webtoons.com
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class WebtoonsSource(CommonSource):
    name = "Webtoons"
    domains = ["https://webtoons.com"]
    headers = {"Referer": "https://webtoons.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: BeautifulSoup | None = None

        title_no_index = url.index("?title_no=") + len("?title_no=")
        title_no_end_index: int | None = url.find("&", title_no_index)
        if title_no_end_index == -1:  # if '&' not found in url
            title_no_end_index = None

        self._title_no = int(url[title_no_index:title_no_end_index])

        self._title_path = "/".join(url.split("/")[3:6])

    def _fetch_metadata(self) -> BaseMetadata:
        page = self._get_desktop_soup()
        title = page.select_one('meta[property="og:title"]')["content"]
        authors: list[str] = [
            s.strip()
            for s in page.select_one('meta[property="com-linewebtoon:webtoon:author"]')[
                "content"
            ].split("/")
        ]
        description: str = page.select_one("#content .summary").text
        cover_art_el = page.select_one("#content .detail_body.banner")

        if cover_art_el is None:
            # canvas challenge webtoons can have multiple genres
            # and have different covers
            cover_art_el = page.select_one("#content .detail_header.challenge img")

            cover_art = cover_art_el["src"]
        else:
            art_start_idx = cover_art_el["style"].find("url('") + len("url('")
            art_end_idx = cover_art_el["style"].find("')", art_start_idx)

            cover_art = cover_art_el["style"][art_start_idx:art_end_idx]

        genres_els = list(page.select(".info .genre"))

        for el in genres_els:
            span = el.find_all("span")
            for s in span:
                s.replace_with("")

        genres = [el.text for el in page.select(".info .genre")]

        return BaseMetadata(
            title,
            authors,
            f"https://www.webtoons.com/{self._title_path}/list?title_no={self._title_no}",
            genres,
            description,
            cover_art,
        )

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = self._get_soup()
        titles = [str(e.next_element) for e in soup.select("p.sub_title > span.ellipsis")]

        links: list[str] = [e["href"] for e in soup.select('a[class^="NPI=a:list"]')]

        chapters = [BaseChapter(t, u) for t, u in zip(titles, links)]
        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        images: list[str] = []
        for c in soup.select("div#_imageList > img"):
            images.append(c["data-url"])
        return images

    def _get_soup(self) -> BeautifulSoup:
        if self._soup:
            return self._soup

        # mobile serves all chapters in one page
        mobile_url = f"https://m.webtoons.com/{self._title_path}/list?title_no={self._title_no}"

        self._soup = BeautifulSoup(
            requests.get(mobile_url, headers=self.headers).text,
            "lxml",
        )
        return self._soup

    def _get_desktop_soup(self) -> BeautifulSoup:
        desktop_url = f"https://www.webtoons.com/{self._title_path}/list?title_no={self._title_no}"
        return BeautifulSoup(requests.get(desktop_url, headers=self.headers).text, "lxml")

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://www.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://m.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://www.webtoons.com/.*/viewer\?title_no=.*", url)
        )


def get_class() -> type[CommonSource]:
    return WebtoonsSource
