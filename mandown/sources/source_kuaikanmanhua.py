"""
Source file for kuaikanmanhua.com
"""
# pylint: disable=invalid-name

import json
import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class KuaiKanManhuaSource(CommonSource):
    name = "快看漫画 (Kuaikan Manhua)"
    domains = ["https://www.kuaikanmanhua.com"]
    # headers = {"Referer": "https://www.kuaikanmanhua.com/"}

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)  # we make a GET request here which is not ideal
        self.url = f"https://www.kuaikanmanhua.com/web/topic/{self.id}"
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        title: str = soup.select_one("h3.title").text
        authors: list[str] = [soup.select_one("div.nickname").text.strip()]
        genres: list[str] = []  # no genres accessible from the list page on this site
        cover_art: str = soup.select_one("img.img")["src"]

        description = soup.select_one("div.detailsBox > p").text.strip().lstrip("漫画简介:").strip()

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        text = self._get_scripts()
        soup = BeautifulSoup(text, "lxml")
        array_start = text.index("Array(")
        next_https = text.index('"https:', array_start)
        previous_quote = text.rindex('"', array_start, next_https)
        prev_prev_quote = text.rindex(
            '"', array_start, previous_quote
        )  # this should be the quote of the first el in what we want

        end = text.index("{}", next_https)
        last_comma = text.rindex(",", next_https, end)

        constructed = f"[{text[prev_prev_quote:last_comma]}]"
        strings: list[str | int] = json.loads(constructed)

        # Array(7),"都市","热血","投稿","1.起源","https://...
        # we want to get "1.起源","https://...
        # but "都市","热血","投稿" may not be there

        # the first chapter does not have its id in the array
        first_chapter_id = int(soup.select_one("a.firstBtn")["data-href"].split("/")[-1])
        strings.insert(0, first_chapter_id)

        # if it is an int, it must be the chapter id, then the title
        chapters: list[BaseChapter] = []
        for i, string in enumerate(strings):
            if isinstance(string, int) and string >= 459:  # magic number from binary search
                # there are some weird numbers like 257 that pop up and are not chapters
                chapters.append(
                    BaseChapter(
                        strings[i + 1], f"https://www.kuaikanmanhua.com/webs/comic-next/{string}"
                    )
                )
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        text = requests.get(chapter.url).text
        js_start = text.index("config:{_app:")
        next_sign = text.index("?sign=", js_start)
        prev_quote = text.rindex('"', js_start, next_sign)
        last_sign = text.rindex("?sign=", js_start)
        last_comma = text.index(",", last_sign)
        constructed = f"[{text[prev_quote:last_comma]}]"
        strings: list[str] = json.loads(constructed)
        return [s for s in strings if isinstance(s, str)]  # there may be ints

    @classmethod
    def url_to_id(cls, url: str) -> str:
        items = list(filter(None, url.split("/")))
        # e.g., for https://www.kuaikanmanhua.com/web/topic/16222/
        # we want '16222'
        # for https://www.kuaikanmanhua.com/webs/comic-next/540156
        # we want to crawl the page and find the link back to the ID

        if "topic" in items:
            return int(items[4])
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        return soup.select_one(".tools-step > a.step-topic").attrs["href"].split("/")[-1]

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(
                r"https://www.kuaikanmanhua.com/((web/topic/\d*/?)|(webs/comic-next/\d+))", url
            )
        )


def get_class() -> type[CommonSource]:
    return KuaiKanManhuaSource
