from dataclasses import dataclass
from typing import Final, Optional
import textwrap


class SourceNotOverriddenError(Exception):
    pass


@dataclass
class MangaMetadata:
    title: str
    authors: list[str]
    url: str


@dataclass
class Chapter:
    title: str
    url: str
    images: Optional[list[str]] = None


class BaseSource:
    metadata: Optional[MangaMetadata] = None
    chapters: list[Chapter] = []
    USER_AGENT: Final = (
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"
    )

    def __init__(self, url: str):
        """
        An object representing a manga from a specific source
        """
        self.url = url

    def get_metadata(self) -> MangaMetadata:
        """
        Fetch and return title, author, and url of the manga.
        """
        raise SourceNotOverriddenError("Metadata getter not overridden")

    def get_chapter_list(self) -> list[Chapter]:
        """
        Fetch and return a list of chapter titles and their URL in ascending order.
        """
        raise SourceNotOverriddenError("Chapter list getter not overridden")

    def get_chapter_image_list(self, chapter: Chapter) -> Chapter:
        """
        Given a chapter, fetch and return a list of image URLs in ascending order for that chapter.
        """
        raise SourceNotOverriddenError("Image URL getter not overridden")

    @classmethod
    def check_url(cls, url: str) -> bool:
        """
        Returns whether the url given matches that of the site and is processable
        """
        raise SourceNotOverriddenError("URL checker not overridden")

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""\
            title: {self.metadata.title}
            authors: {self.metadata.authors}
            url: {self.metadata.url}
            chapters: {len(self.chapters)}\
        """
        )


def get_class() -> type[BaseSource]:
    return BaseSource
