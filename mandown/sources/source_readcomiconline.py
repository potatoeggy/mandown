"""
Source file for readcomiconline.li
"""
# pylint: disable=invalid-name

import binascii
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
        description_maybe = soup.select_one("p[style='text-align: justify;']")
        description = str(description_maybe.text if description_maybe else "")
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
        return list(reversed(chapters))

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        text = requests.get(chapter.url).text

        images: list[str] = []
        start = 0
        while (index := text.find("lstImages.push(", start)) != -1:
            s_index = index + len("lstImages.push(") + 1
            e_index = text.find(");", s_index) - 1  # could be single or double quotes
            images.append(self.beau(text[s_index:e_index]))
            start = e_index
        return images

    @classmethod
    def url_to_id(cls, url: str) -> str:
        segments = url.split("/")
        for i, s in enumerate(segments):
            if s == "Comic":
                return segments[i + 1]
        raise ValueError("Invalid comic URL")

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://readcomiconline.li/Comic/.*", url))

    @staticmethod
    def beau(url: str) -> str:
        """
        Deobfuscator
        copied from https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/readcomiconline.py

        i had to relicense to GPLv2 for this >:(
        """
        url = url.replace("_x236", "d").replace("_x945", "g")

        if url.startswith("https"):
            return url

        url, sep, rest = url.partition("?")
        containsS0 = "=s0" in url
        url = url[: -3 if containsS0 else -6]
        url = url[4:22] + url[25:]
        url = url[0:-6] + url[-2:]
        url = binascii.a2b_base64(url).decode()
        url = url[0:13] + url[17:]
        url = url[0:-2] + ("=s0" if containsS0 else "=s1600")
        return f"https://2.bp.blogspot.com/{url}{sep}{rest}"


def get_class() -> type[BaseSource]:
    return ReadComicOnlineSource
