"""
Source file for readcomiconline.li
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup
from mandown.iohandler import UndetectedDriver

from .base_source import BaseSource, Chapter, MangaMetadata


class ReadComicOnlineSource(BaseSource):
    name = "ReadComicOnline"
    domains = ["https://readcomiconline.li"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self.driver = UndetectedDriver()
        self.title = ""

    def fetch_metadata(self) -> MangaMetadata:
        soup = BeautifulSoup(
            self.driver.get(f"https://readcomiconline.li/Comic/{self.id}"),
            features="lxml",
        )

        title = str(soup.select_one("a.bigChar").text)
        self.title = title
        author = [
            str(
                # this site uses "Various" if there's more than one author
                soup.select_one("a[href^='/Writer']").text
            )
        ]
        genres: list[str] = [str(e.text) for e in soup.select("a[href^='/Genre']")]
        desc_element = soup.select_one("p[style='text-align: justify;']")

        description = str(desc_element.text) if desc_element else ""
        cover = self.domains[0] + str(soup.find("link")["href"])

        return MangaMetadata(title, author, self.url, genres, description, cover)

    def fetch_chapter_list(self) -> list[Chapter]:
        soup = BeautifulSoup(
            self.driver.get(f"https://readcomiconline.li/Comic/{self.id}"),
            features="lxml",
        )

        chapters: list[Chapter] = []
        for e in soup.select("td > a"):
            chapters.append(
                Chapter(
                    self,
                    next(e.children).text.strip()[len(self.title) + 1 :],
                    self.domains[0] + e["href"],
                )
            )
        return list(reversed(chapters))

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        text = self.driver.get(chapter.url)

        images: list[str] = []
        start = 0
        while (index := text.find("lstImages.push(", start)) != -1:
            s_index = index + len('lstImages.push("')
            e_index = text.find('");', s_index)
            images.append(text[s_index:e_index])
            start = e_index
        return images

    @classmethod
    def url_to_id(cls, url: str) -> str:
        *_, last_item = filter(None, url.split("/"))
        return last_item

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://readcomiconline.li/Comic/.*", url))


def get_class() -> type[BaseSource]:
    return ReadComicOnlineSource
