"""
Source file for readmanganato.com
"""
# pylint: disable=invalid-name

import re
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from ..base import BaseChapter, BaseMetadata
from .common_source import CommonSource


class MangaNatoSource(CommonSource):
    name = "ComicFury"
    domains = [
        "https://thecomicseries.com",
        "https://comicfury.com",
    ]

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.id = self.url_to_id(url)

    def _fetch_metadata(self) -> BaseMetadata:
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

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        soup = BeautifulSoup(
            requests.get(f"https://comicfury.com/read/{self.id}/archive").text,
            "lxml",
        )

        chapters: list[BaseChapter] = [
            BaseChapter(e.text.strip(), f"https://comicfury.com{e['href']}")
            for e in soup.select("a:has(.archive-chapter)")
        ]
        return chapters

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        soup = BeautifulSoup(requests.get(chapter.url).text, "lxml")
        pages = soup.select(".archive-comics > a")
        # href is of form /read/title/comics/number
        first_page_id = pages[0]["href"].split("/")[-1]

        # /comic.php?action=addsubscription&amp;cid=number
        comic_id = soup.select_one(".webcomic-subscribe")["href"].split("=")[-1]

        # we need the total number of pages
        page_list_urls = soup.select("div.archive-pages .vfpage")
        index = None
        if page_list_urls:
            for i, el in enumerate(page_list_urls):
                if i == 0:
                    continue
                if "vfpagecurrent" in el["class"]:
                    # these appear twice so this is how we differentiate them
                    index = i - 1
                    break

        if index is None:
            num_pages = len(pages)
        else:
            soup3 = BeautifulSoup(
                requests.get(f"https://comicfury.com{page_list_urls[index]['href']}").text,
                "lxml",
            )
            # index is zero-indexed
            num_pages = len(pages) * (index + 1) + len(soup3.select(".archive-comics > a"))

        # their api only returns images after the first page
        # so we have to fetch it ourselves
        soup4 = BeautifulSoup(
            requests.get(f"https://comicfury.com{pages[0]['href']}").text,
            "lxml",
        )
        first_page = soup4.select_one(".is--comic-content img")["src"]

        # call their api
        page_id = first_page_id
        all_images: list[str] = [first_page]
        while len(all_images) < num_pages:
            data = requests.get(
                f"https://comicfury.com/api.php?url=webcomic/id/{comic_id}/comicid/{page_id}/getonsitereadercomics"
            ).json()
            if not data["status"] or data["error_code"]:
                raise RuntimeError(
                    "ComicFury did not give an expected response."
                    "Please report this issue to GitHub."
                )
            page_id = data["data"]["newLastComicId"]

            soup2 = BeautifulSoup(data["data"]["html"], "lxml")
            cur_images = [img["src"] for img in soup2.select(".is--comic-content img")]
            all_images.extend(cur_images)
            if data["data"]["endsAtLastComic"]:
                break
        return all_images

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
            or re.match(r"https://comicfury.com/read/.*/comics/*", url)
        )


def get_class() -> type[CommonSource]:
    return MangaNatoSource
