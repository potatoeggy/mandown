"""
Source file for bato.to
"""

import html
import json
import re
from typing import cast

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class BatotoSource(CommonSource):
    name = "Bato.to"
    domains = ["https://bato.to"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)  # we make a GET request here which is not ideal
        self.url = f"https://bato.to/title/{self.id}"
        self._scripts: str | None = None

    def _fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        cover_art_el = soup.select_one("img.not-prose")
        title = cast(str, cover_art_el["alt"])
        cover_art = cast(str, cover_art_el["src"])
        authors = list({strip_parentheses(item.text) for item in soup.select("div.mt-2 a")})
        genres = [
            strip_parentheses(g.text)
            for g in soup.select(
                "div.space-y-2 > div.flex.items-center.flex-wrap > span > :nth-child(1)"
            )
        ]
        description = soup.select_one("astro-island > div > .prose > .limit-html-p").text.strip()

        return BaseMetadata(title, authors, self.url, genres, description, cover_art)

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(self._get_scripts(), "lxml")

        chapters: list[BaseChapter] = []
        for item in soup.select('div[name="chapter-list"] div.space-x-1 > a:nth-child(1)'):
            link = cast(str, item["href"])
            title = item.text
            chapters.append(BaseChapter(title, f"https://bato.to{link}?load=2"))
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")

        """
        It looks something like:
        {'pageOpts': [0, {'load': [0, '2'], 'marg': [0, '0'], 'zoom': [0, '0']}], 'imageFiles': [1,
        '[[0,"https://xfs-n03.xfsbb.com/comic/7006/fbf/65ac7d07a811b44f5e9abfbf/45869815_2560_2824_374174.webp"]]'
        ], 'urlP': [0, 0]}
        """
        data = json.loads(
            html.unescape(
                soup.select_one('astro-island[component-url^="/_astro/ImageList"]')["props"]
            )
        )

        images: list[str] = []
        for image in json.loads(data["imageFiles"][1]):
            images.append(image[1])
        return images

    @classmethod
    def url_to_id(cls, url: str) -> str:
        items = list(filter(None, url.split("/")))

        # e.g., for https://bato.to/title/115663-my-not-so-fair-lady-is-doomed-but-not-if-i-can-help-it-official/2950514-ch_15
        # we want "115663-my-not-so-fair-lady-is-doomed-but-not-if-i-can-help-it-official"

        return items[3]

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(re.match(r"https://bato.to/title/.*", url))


def get_class() -> type[CommonSource]:
    return BatotoSource


def strip_parentheses(text: str) -> str:
    index = text.find("(")
    if index != -1:
        return text[:index].strip()
    return text.strip()
