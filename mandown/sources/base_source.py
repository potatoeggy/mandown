# pylint: disable=no-member

import re
import textwrap
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Callable, Final

from lxml import etree
from lxml.builder import ElementMaker


class SourceNotOverriddenError(Exception):
    pass


@dataclass(frozen=True)
class MangaMetadata:
    OPF_MAP = {"opf": "http://www.idpf.org/2007/opf"}

    title: str
    authors: list[str]
    url: str
    genres: list[str]
    description: str
    cover_art: str

    def to_opf(self, /, pretty_print: bool = False) -> str:
        E = ElementMaker()  # pylint: disable=invalid-name
        M = ElementMaker(  # pylint: disable=invalid-name
            namespace="http://purl.org/dc/elements/1.1/", nsmap=self.OPF_MAP
        )

        els_genres = [M.subject(i) for i in self.genres]
        els_authors = [M.creator(i) for i in self.authors]

        package = E.package(
            M.metadata(
                M.title(self.title),
                *els_authors,
                M.contributor("mandown", role="bkp"),
                M.description(self.description),
                M.identifier(self.url, scheme="URL"),
                M.language("eng"),
                *els_genres,
                E.meta(name="mandown:cover", content=self.cover_art),
            ),
            E.guide(E.reference(type="cover", title="Cover", href="cover")),
            nsmap=self.OPF_MAP["opf"],
            version="2.0",
        )

        return etree.tostring(
            package, xml_declaration=True, encoding="utf-8", pretty_print=pretty_print
        ).decode("utf-8")

    @classmethod
    def from_opf_tree(cls, package: etree._Element) -> "MangaMetadata":
        metadata = package[0]

        def dc_find_all(tag: str) -> list[str]:
            full_tag = "{http://purl.org/dc/elements/1.1/}" + tag
            return list(map(lambda e: e.text or "", metadata.findall(full_tag)))

        try:
            title = dc_find_all("title")[0]
            authors = dc_find_all("creator")
            description = dc_find_all("description")[0]
            url = dc_find_all("identifier")[0]
            genres = dc_find_all("genres")

            metas = metadata.findall("meta")
            meta_dict = {e.get("name"): e.get("content") for e in metas}

            cover_art = meta_dict["mandown:cover"] or ""
            return MangaMetadata(title, authors, url, genres, description, cover_art)
        except IndexError as err:
            raise IndexError("Missing mandatory metadata tag") from err
        except KeyError as err:
            raise KeyError("Missing mandatory metadata tag") from err

    @classmethod
    def from_file(cls, path: Path | str) -> "MangaMetadata":
        package = etree.parse(path).getroot()
        return cls.from_opf_tree(package)

    @classmethod
    def from_str(cls, string: str) -> "MangaMetadata":
        package = etree.fromstring(bytes(string, encoding="utf-8"))
        return cls.from_opf_tree(package)


@dataclass
class Chapter:
    # quotes are used to prevent syntax error
    # pylint: disable=used-before-assignment
    source: InitVar["BaseSource"]  # type: ignore
    title: str
    url: str
    headers: dict[str, str] | None = None

    _image_fetcher: Callable[
        ["Chapter"], list[str]  # type: ignore # pylint: disable=undefined-variable
    ] = field(init=False)
    _images: list[str] = field(init=False, default_factory=list)

    def __post_init__(self, source: "BaseSource") -> None:  # type: ignore
        self._image_fetcher = source.fetch_chapter_image_list
        # get rid of all forbidden chars in filenames
        self.title_sanitised = re.sub(r"[\\\/:*?<>|]", "_", self.title)

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
    domains = ["Source domains goes here"]

    _metadata: MangaMetadata | None = None
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
            genres: {self.metadata.genres}
            description:
                {(chr(10) + " "*16).join(self.metadata.description.split(chr(10)))}
            chapters: {len(self.chapters)}\
            """
        )


def get_class() -> type[BaseSource]:
    return BaseSource
