"""
Source file for mangadex.org
"""
# pylint: disable=invalid-name

import re
import time

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class MangaDexSource(CommonSource):
    name = "MangaDex"
    domains = ["https://mangadex.org"]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._soup: BeautifulSoup | None = None
        self.lang_code = ""

        # https://api.mangadex.org/manga/de4b3c43-5243-4399-9fc3-68a3c0747138
        self.id = self.url.split("/")[4]
        if self.url.startswith("https://mangadex.org/chapter"):
            r: dict = self._get(f"https://api.mangadex.org/chapter/{self.id}").json()["data"][
                "relationships"
            ]
            self.id: str = next(filter(lambda i: i["type"] == "manga", r))["id"]  # type: ignore

    def _fetch_metadata(self) -> BaseMetadata:
        # TODO: support non-English downloads
        r = self._get(
            f"https://api.mangadex.org/manga/{self.id}"
            "?includes[]=author&includes[]=cover_art&includes[]=artist"
        ).json()

        metadata: dict = r["data"]

        # use english if possible, otherwise use the first language that appears
        self.lang_code = (
            "en"
            if "en" in metadata["attributes"]["title"]
            else next(iter(metadata["attributes"]["title"]))
        )
        title: str = metadata["attributes"]["title"][self.lang_code]

        if metadata["attributes"]["description"]:
            description: str = metadata["attributes"]["description"][self.lang_code]

            # strip trailing spaces on each line
            description = "\n".join(s.strip() for s in description.split("\n"))
        else:
            description = ""

        authors: set[str] = set()
        cover_art = ""
        for d in metadata["relationships"]:
            if d["type"] == "author" or d["type"] == "artist":
                authors.add(d["attributes"]["name"])
            elif d["type"] == "cover_art":
                # pylint: disable=line-too-long
                cover_art = (
                    "https://uploads.mangadex.org/covers/"
                    f"{self.id}/{d['attributes']['fileName']}"
                )

        genres: list[str] = []
        for d in metadata["attributes"]["tags"]:
            tag = d["attributes"]["group"]
            if tag == "genre" or tag == "theme":
                genres.append(d["attributes"]["name"][self.lang_code])

        return BaseMetadata(
            title,
            list(authors),
            f"https://mangadex.org/title/{self.id}",
            genres,
            description,
            cover_art,
        )

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        # for some reason *sometimes* it goes all name/service not found
        r = self._get(
            f"https://api.mangadex.org/manga/{self.id}/"
            f"feed?limit=500&translatedLanguage[]={self.lang_code}"
            "&order[volume]=asc&order[chapter]=asc"
        ).json()

        chapters: list[BaseChapter] = []
        for i, c in enumerate(r["data"]):
            chapter_title: str = c["attributes"]["title"] or f"Chapter {c['attributes']['chapter']}"
            chapter_slug: str = f"{i}-{slugify(chapter_title)}"
            chapters.append(
                BaseChapter(
                    chapter_title,
                    f"https://mangadex.org/chapter/{c['id']}",
                    chapter_slug,
                )
            )
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        *_, chapter_id = chapter.url.split("/")
        r = self._get(f"https://api.mangadex.org/at-home/server/{chapter_id}").json()
        base_url = r["baseUrl"]
        chapter_hash = r["chapter"]["hash"]

        images: list[str] = []
        for p in r["chapter"]["data"]:
            images.append(f"{base_url}/data/{chapter_hash}/{p}")
        return images

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://mangadex.org/title/.*", url)
            or re.match(r"https://mangadex.org/chapter/.*", url)
        )

    @staticmethod
    def _get(url: str) -> requests.Response:
        """
        A wrapper of requests.get for MangaDex with
        rudimentary rate-limit processing
        """
        for _ in range(3):
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                break
            elif r.status_code == 404:
                raise RuntimeError(
                    "This chapter is not downloadable from MangaDex. If you "
                    "believe this to be an error, please open a GitHub issue."
                )
            time.sleep(1)
        else:
            raise RuntimeError("MangaDex is probably rate-limiting us, try again later?")
        return r


def get_class() -> type[CommonSource]:
    return MangaDexSource
