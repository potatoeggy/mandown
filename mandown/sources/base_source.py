from collections import defaultdict
from typing import final

from ..base import BaseChapter, BaseMetadata


class BaseSource:
    """
    An object representing network state for fetching data of a comic.
    """

    name = "Source name goes here"
    domains = ["Source domains goes here"]
    headers: dict[str, str] = {}

    _metadata: BaseMetadata | None = None
    _chapters: list[BaseChapter] = []

    def __init__(self, url: str):
        self.url = url

    @final
    @property
    def metadata(self) -> BaseMetadata:
        """
        Return the metadata of the comic, fetching and caching it if necessary.
        """
        if self._metadata:
            return self._metadata
        self._metadata = self.fetch_metadata()
        return self._metadata

    @final
    @property
    def chapters(self) -> list[BaseChapter]:
        """
        Return the chapter list of the comic, fetching and caching it if necessary.
        """
        if self._chapters:
            return self._chapters
        self._chapters = self.fetch_chapter_list()
        return self._chapters

    @final
    def fetch_metadata(self) -> BaseMetadata:
        """
        Fetch and return title, author, and url of the comic.
        """
        return self._fetch_metadata()

    @final
    def fetch_chapter_list(self) -> list[BaseChapter]:
        """
        Fetch and return a list of chapter titles and their URL in ascending order.

        Check for duplicate chapters and disambiguate them.
        """
        chapters = self._fetch_chapter_list()

        chapter_dupes = defaultdict[str, int](lambda: 1)  # slug -> count
        for i, c in enumerate(chapters):  # this is O(n^2) but n is small
            if any(c.slug == x.slug or c.title == x.title for x in chapters[:i]):
                chapter_dupes[c.slug] += 1
                c.slug = f"{c.slug}-{chapter_dupes[c.slug]}"
                c.title = f"{c.title} ({chapter_dupes[c.slug]})"

        return chapters

    @final
    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        """
        Given a chapter link, fetch and return a list of image URLs in ascending
        order for that chapter.
        """
        return self._fetch_chapter_image_list(chapter)

    # override these below!
    def _fetch_metadata(self) -> BaseMetadata:
        """
        Fetch and return title, author, and url of the comic.
        """
        raise NotImplementedError("Metadata getter not overridden")

    def _fetch_chapter_list(self) -> list[BaseChapter]:
        """
        Fetch and return a list of chapter titles and their URL in ascending order.
        """
        raise NotImplementedError("Chapter list getter not overridden")

    def _fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        """
        Given a chapter link, fetch and return a list of image URLs in ascending
        order for that chapter.
        """
        raise NotImplementedError("Image URL getter not overridden")

    @staticmethod
    def check_url(url: str) -> bool:
        """
        Returns whether the url given matches that of the site and is processable
        """
        raise NotImplementedError("URL checker not overridden")


def get_class() -> type[BaseSource]:
    return BaseSource
