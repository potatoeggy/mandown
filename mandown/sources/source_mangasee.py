"""
Source file for mangasee123.com
"""
# pylint: disable=invalid-name

import json
import re
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from .base_source import BaseSource, Chapter, MangaMetadata


class MangaSeeSource(BaseSource):
    name = "MangaSee"

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self._scripts: Optional[str] = None

    def fetch_metadata(self) -> MangaMetadata:
        # all of the metadata is available in the <script type="application/ld+json"> element
        # so are the chapters
        soup = BeautifulSoup(self._get_scripts(), "html.parser")
        metadata_json: dict = json.loads(
            soup.find("script", type="application/ld+json").next_element
        )["mainEntity"]

        title: str = metadata_json["name"]
        authors: list[str] = metadata_json["author"]
        # genres: list[str] = metadata_json["genre"]

        return MangaMetadata(title, authors, self.url)

    def fetch_chapter_list(self) -> list[Chapter]:
        feed = feedparser.parse(
            f"https://mangasee123.com/rss/{self.id}.xml", agent=self.USER_AGENT
        )

        chapters = []
        for c in feed["entries"]:
            chapter_title = str(c["title"]).lstrip(self.metadata.title).strip()
            chapters.append(Chapter(self, chapter_title, c["link"]))

        chapters.reverse()
        return chapters

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "html.parser")
        full_js = str(
            soup.find("script", type="application/ld+json")
            .find_next("script")
            .next_element
        )

        index_start = full_js.index("vm.CurChapter =") + len("vm.CurChapter =")
        index_end = full_js.index(";", index_start)
        chapter_details: dict = json.loads(full_js[index_start:index_end])

        index_start = full_js.index("vm.CurPathName =") + len("vm.CurPathName =")
        index_end = full_js.index(";", index_start)

        domain: str = json.loads(full_js[index_start:index_end])
        num_pages = int(chapter_details["Page"])
        chapter_number: str = chapter.title.split()[-1]
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

    def _get_scripts(self) -> str:
        if self._scripts:
            return self._scripts

        self._scripts = requests.get(self.url).text
        return self._scripts

    @classmethod
    def url_to_id(cls, url: str) -> str:
        # converts page url to id
        # e.g. https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To
        # to Kaguya-Wants-To-Be-Confessed-To
        *_, last_item = filter(None, url.split("/"))
        # TODO: switch to regex for better reliability
        # in case they add weird tags to the end like tracking
        return last_item


def get_class() -> type[BaseSource]:
    return MangaSeeSource
