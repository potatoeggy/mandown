"""
Source file for readmanganato.com
"""
# pylint: disable=invalid-name

import re
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .base_source import BaseSource


class MangaNatoSource(BaseSource):
    name = "ComicFury"
    domains = [
        "https://thecomicseries.com",
        "https://comicfury.com",
    ]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)

    def fetch_metadata(self) -> BaseMetadata:
        soup = BeautifulSoup(
            requests.get(f"https://comicfury.com/comicprofile.php?url={self.id}").text,
            "lxml",
        )

        title = str(soup.select_one("div.authorname").text).strip()
        authors = [str(a.text).strip() for a in soup.select("a.authorname")]
        genres = [str(g.text).strip() for g in soup.select(".description-tags > a")]
        description_maybe = soup.select_one(".pccontent:has(.description-tags)")

        if description_maybe is not None:
            for div in description_maybe.find_all("div"):
                div.replace_with("\n")
        description = str(description_maybe.text).strip()
        cover = f"https://comicfury.com{str(soup.select_one('.profile-avatar > img')['src'])}"

        return BaseMetadata(title, authors, self.url, genres, description, cover)

    def fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(
            requests.get(f"https://comicfury.com/read/{self.id}/archive").text,
            "lxml",
        )

        chapters: list[BaseChapter] = [
            BaseChapter(e.text.strip(), f"https://comicfury.com{e['href']}")
            for e in soup.select("a:has(.archive-chapter)")
        ]
        return chapters

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        pages = soup.select(".archive-comics > a")
        # href is of form /read/title/comics/number
        first_page_id = pages[0]["href"].split("/")[-1]

        # /comic.php?action=addsubscription&amp;cid=number
        comic_id = soup.select_one(".webcomic-subscribe")["href"].split("=")[-1]

        # call their api
        data = requests.get(
            f"https://comicfury.com/api.php?url=webcomic/id/{comic_id}/comicid/{first_page_id}/getonsitereadercomics"
        ).json()
        if not data["status"] or data["error_code"]:
            raise RuntimeError(
                "ComicFury did not give an expected response. Please report this issue to GitHub."
            )

        soup2 = BeautifulSoup(data["data"]["html"], "lxml")
        return [img["src"] for img in soup2.select(".is--comic-content img")]

    @classmethod
    def url_to_id(cls, url: str) -> str:
        parsed = urlparse(url)
        if parsed.netloc == "comicfury.com":
            # it is in the form comicfury.com/comicprofile.php?url=name
            # or comicfury.com/read/*/comics/*
            if parsed.path.startswith("/read/"):
                return parsed.path.split("/")[2]
            return parse_qs(parsed.query)["url"][0]
        # it is in the form name.thecomicseries.com
        return parsed.netloc.split(".")[0]

    @staticmethod
    def check_url(url: str) -> bool:
        return bool(
            re.match(r"https://comicfury\.com/comicprofile\.php.*", url)
            or re.match(r"https://.*\.thecomicseries\.com.*", url)
            or re.match(r"https://comicfury.com/read/*/comics/*", url)
        )


def get_class() -> type[BaseSource]:
    return MangaNatoSource
