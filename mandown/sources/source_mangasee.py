"""
Source file for mangasee123.com
"""
# pylint: disable=invalid-name

import json
import re

import feedparser
import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class MangaSeeSource(CommonSource):
    name = "MangaSee"
    domains = ["https://mangasee123.com"]
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        # all of the metadata is available in the <script type="application/ld+json"> element
        # so are the chapters
        soup = BeautifulSoup(self._get_scripts(), "lxml")
        metadata_json: dict = json.loads(
            soup.find("script", type="application/ld+json").next_element
        )["mainEntity"]

        title: str = metadata_json["name"]

        authors_html = soup.select('a[href^="/search/?author"]')
        authors: list[str] = [a.next_element for a in authors_html]

        genres: list[str] = metadata_json["genre"]

        description_html = soup.select_one("div.top-5.Content")
        description = str(description_html.next_element).strip()

        cover_art = soup.select_one('div[style="padding-right:0px;"] img.bottom-5')["src"]

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        feed = feedparser.parse(f"https://mangasee123.com/rss/{self.id}.xml", agent=self.USER_AGENT)

        chapters = []
        for c in feed["entries"]:
            chapter_title = str(c["title"]).lstrip(self.metadata.title).strip()
            chapters.append(BaseChapter(chapter_title, c["link"]))

        chapters.reverse()
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        full_js = str(
            soup.find("script", type="application/ld+json").find_next("script").next_element
        )

        index_start = full_js.index("vm.CurChapter =") + len("vm.CurChapter =")
        index_end = full_js.index(";", index_start)
        chapter_details: dict = json.loads(full_js[index_start:index_end])

        index_start = full_js.index("vm.CurPathName =") + len("vm.CurPathName =")
        index_end = full_js.index(";", index_start)

        domain: str = json.loads(full_js[index_start:index_end])
        num_pages = int(chapter_details["Page"])
        chapter_number = chapter.title.split()[-1]
        # pad to 4 excluding decimal places
        pad_zero = max(4 - len(str(int(float(chapter_number)))), 0)

        image_list = [
            f"https://{domain}/manga/{self.id}/{'0' * pad_zero}{chapter_number}-{i:03}.png"
            for i in range(1, num_pages + 1)
        ]
        return image_list

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://mangasee123.com/manga/.*", url))

    @classmethod
    def url_to_id(cls, url: str) -> str:
        # converts page url to id
        # e.g. https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To
        # to Kaguya-Wants-To-Be-Confessed-To
        *_, last_item = filter(None, url.split("/"))
        return last_item


def get_class() -> type[CommonSource]:
    return MangaSeeSource
