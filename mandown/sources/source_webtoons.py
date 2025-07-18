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
        self.webtoon_type = "canvas" if "/canvas/" in url or "/challenge/" in url else "webtoon"

    def _fetch_metadata(self) -> BaseMetadata:
        page = self._get_soup()
        title = page.select_one('h2.title').text.strip()
        print(page.select_one('meta[property="com-linewebtoon:webtoon:author"]'), self.webtoon_type)
        authors: list[str] = [
            s.strip()
            for s in page.select_one('meta[property=":webtoon:author"]' if self.webtoon_type == "webtoon" else 'meta[property="com-linewebtoon:webtoon:author"]')[
                "content"
            ].split("/")[:2] # up to 2 authors
        ]
        description: str = page.select_one("a.summary._summary").text.strip()
        cover_art_el = page.select_one(".detail_info_wrap > .img_area img")
        cover_art = cover_art_el["src"]

        genres = [el.text.strip("#") for el in page.select("ul.tag_box li.tag")]

        return BaseMetadata(
            title,
            authors,
            f"https://www.webtoons.com/{self._title_path}/list?title_no={self._title_no}",
            genres,
            description,
            cover_art,
        )

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        api_url = f"https://m.webtoons.com/api/v1/{self.webtoon_type}/{self._title_no}/episodes?pageSize=2000"
        res = requests.get(api_url, headers=self.headers).json()["result"]
        if res["nextCursor"]:
            raise ValueError("Webtoon has more than 2000 episodes. This is definitely a bug. Please report it to the developer.")
        
        chapters = [
            BaseChapter(
                e["episodeTitle"],
                f"https://www.webtoons.com{e['viewerLink']}"
            )
            for e in res["episodeList"]
        ]
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

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://www.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://m.webtoons.com/.*/list\?title_no=.*", url)
            or re.match(r"https://www.webtoons.com/.*/viewer\?title_no=.*", url)
        )


def get_class() -> type[CommonSource]:
    return WebtoonsSource
