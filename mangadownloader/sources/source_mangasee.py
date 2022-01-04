"""
Source file for MangaSee
"""

import json
import re
import feedparser
from bs4 import BeautifulSoup
import requests
from .base_source import BaseSource, Chapter, MangaMetadata


class MangaSeeSource(BaseSource):
    def __init__(self, url: str) -> None:
        BaseSource.__init__(self, url)
        self.id = self.url_to_id(url)
        self.scripts: str | None = None

    def get_metadata(self) -> MangaMetadata:
        # all of the metadata is available in the <script type="application/ld+json"> element
        # so are the chapters
        if self.metadata:
            return self.metadata

        soup = BeautifulSoup(self._get_scripts(), features="lxml")
        metadata_json: dict = json.loads(
            soup.find("script", type="application/ld+json").next_element
        )["mainEntity"]

        title: str = metadata_json["name"]
        authors: list[str] = metadata_json["author"]
        # genres: list[str] = metadata_json["genre"]

        self.metadata = MangaMetadata(title, authors, self.url)

        return self.metadata

    def get_chapter_list(self) -> list[Chapter]:
        if self.chapters:
            return self.chapters

        feed = feedparser.parse(
            f"https://mangasee123.com/rss/{self.id}.xml", agent=self.USER_AGENT
        )

        self.chapters = []
        for c in feed["entries"]:
            chapter_title = str(c["title"]).lstrip(self.get_metadata().title).strip()
            self.chapters.append(Chapter(chapter_title, c["link"]))

        self.chapters.reverse()
        return self.chapters

    def get_chapter_image_list(self, chapter: Chapter) -> Chapter:
        if chapter.images:
            return chapter

        self.get_chapter_list()

        soup = BeautifulSoup(requests.get(chapter.url).text, features="lxml")
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
        new_chapter = Chapter(chapter.title, chapter.url, image_list)

        return new_chapter

    @classmethod
    def check_url(cls, url: str) -> bool:
        return bool(re.match(r"https://mangasee123.com/manga/.*", url))

    def _get_scripts(self) -> str:
        if self.scripts:
            return self.scripts

        self.scripts = requests.get(self.url).text
        return self.scripts

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
