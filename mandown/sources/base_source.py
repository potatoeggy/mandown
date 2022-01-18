import textwrap
from dataclasses import InitVar, dataclass, field
from typing import Callable, Final, Optional


class SourceNotOverriddenError(Exception):
    pass


@dataclass(frozen=True)
class MangaMetadata:
    title: str
    authors: list[str]
    url: str


@dataclass
class Chapter:
    # quotes are used to prevent syntax error
    # pylint: disable=used-before-assignment
    source: InitVar["BaseSource"]  # type: ignore
    title: str
    url: str
    headers: Optional[dict[str, str]] = None

    _image_fetcher: Callable[
        ["Chapter"], list[str]  # type: ignore # pylint: disable=undefined-variable
    ] = field(init=False)
    _images: list[str] = field(init=False, default_factory=list)

    def __post_init__(self, source: "BaseSource") -> None:  # type: ignore
        self._image_fetcher = source.fetch_chapter_image_list

    @property
    def images(self) -> list[str]:
        if self._images:
            return self._images
        self._images = self._image_fetcher(self)
        return self._images

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return textwrap.dedent(
            f"""\
        title: {self.title}
        id/url: {self.url}
        images: {self._images}
        headers: {self.headers}\
        """
        )


class BaseSource:
    name = "Source name goes here"

    _metadata: Optional[MangaMetadata] = None
    _chapters: list[Chapter] = []
    USER_AGENT: Final = (
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0"
    )

    def __init__(self, url: str):
        """
        An object representing a manga from a specific source.
        Properties `metadata` and `chapters` will be lazily populated on first access.
        """
        self.url = url

    @property
    def metadata(self) -> MangaMetadata:
        if self._metadata:
            return self._metadata
        self._metadata = self.fetch_metadata()
        return self._metadata

    @property
    def chapters(self) -> list[Chapter]:
        if self._chapters:
            return self._chapters
        self._chapters = self.fetch_chapter_list()
        return self._chapters

    def fetch_metadata(self) -> MangaMetadata:
        """
        Fetch and return title, author, and url of the manga.
        """
        raise SourceNotOverriddenError("Metadata getter not overridden")

    def fetch_chapter_list(self) -> list[Chapter]:
        """
        Fetch and return a list of chapter titles and their URL in ascending order.
        """
        raise SourceNotOverriddenError("Chapter list getter not overridden")

    def fetch_chapter_image_list(self, chapter: Chapter) -> list[str]:
        """
        Given a chapter link, fetch and return a list of image URLs in ascending
        order for that chapter.
        """
        raise SourceNotOverriddenError("Image URL getter not overridden")

    @staticmethod
    def check_url(url: str) -> bool:
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
