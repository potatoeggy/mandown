from dataclasses import dataclass
from typing import Final, NamedTuple, Optional


class SourceNotOverriddenError(Exception):
    pass


@dataclass
class MangaMetadata:
    title: str
    authors: tuple[str]
    url: str


@dataclass
class Chapter:
    title: str
    url: str
    images: Optional[list[str]] = None


class BaseSource:
    metadata: MangaMetadata = None
    chapters: list[Chapter] = None
    USER_AGENT: Final = (
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"
    )

    def __init__(self):
        pass

    @classmethod
    def get_metadata(self) -> MangaMetadata:
        # return title w/ dataclass for future metadata
        raise SourceNotOverriddenError("Metadata getter not overridden")

    @classmethod
    def get_chapter_list(self) -> list[Chapter]:
        # return dict of chapter title against their URL in ascending order
        # consider using list instead for guaranteed order
        raise SourceNotOverriddenError("Chapter list getter not overridden")

    @classmethod
    def get_chapter_image_list(self) -> list[Chapter]:
        # for a chapter url/number given, get the list of urls for that chapter
        raise SourceNotOverriddenError("Image URL getter not overridden")
