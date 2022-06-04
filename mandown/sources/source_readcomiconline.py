"""
Source file for readcomiconline.li
"""
# pylint: disable=invalid-name

import re

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .base_source import BaseSource


class ReadComicOnlineSource(BaseSource):
    name = "ReadComicOnline"
    domains = ["https://readcomiconline.li"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)

    def fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(
            requests.get(f"https://readcomiconline.li/Comic/{self.id}").text,
            features="lxml",
        )

        title = str(soup.select_one("h3").text)
        author = [
            str(
                # this site uses "Various" if there's more than one author
                soup.select_one("a[href^='/Writer']").text
            )
        ]
        genres: list[str] = [str(e.text) for e in soup.select("a[href^='/Genre']")]
        description = str(soup.select_one("p[style='text-align: justify;']").text)
        cover = self.domains[0] + str(soup.find("link")["href"])

        return BaseMetadata(title, author, self.url, genres, description, cover)

    def fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(
            requests.get(f"https://readcomiconline.li/Comic/{self.id}").text,
            features="lxml",
        )

        chapters: list[BaseChapter] = []
        for e in soup.select("ul.list > li > a"):
            chapters.append(
                BaseChapter(next(e.children).text, self.domains[0] + e["href"])
            )
        return chapters

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        text = requests.get(chapter.url).text

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
