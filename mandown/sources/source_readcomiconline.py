"""
Source file for readcomiconline.li
"""
# pylint: disable=invalid-name


import re

from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from ..undetected import UndetectedDriver
from .base_source import BaseSource


class ReadComicOnlineSource(BaseSource):
    name = "ReadComicOnline"
    domains = ["https://readcomiconline.li"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)
        self.driver = UndetectedDriver()
        self.title = ""

    def fetch_metadata(self) -> BaseMetadata:
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

        return BaseMetadata(title, author, self.url, genres, description, cover)

    def fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(
            self.driver.get(f"https://readcomiconline.li/Comic/{self.id}"),
            features="lxml",
        )

        chapters: list[BaseChapter] = []
        for e in soup.select("td > a"):
            chapters.append(
                BaseChapter(
                    next(e.children).text.strip()[len(self.title) + 1 :],
                    self.domains[0] + e["href"],
                )
            )
        return list(reversed(chapters))

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
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
        segments = url.split("/")
        for i, s in enumerate(segments):
            if s == "Comic":
                return segments[i + 1]
        raise ValueError("Invalid comic")

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://readcomiconline.li/Comic/.*", url))


def get_class() -> type[BaseSource]:
    return ReadComicOnlineSource
