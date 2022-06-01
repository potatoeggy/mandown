# pylint: disable=no-member

from pathlib import Path

from lxml import etree
from lxml.builder import E, ElementMaker

from mandown.sources.base_source import MangaMetadata

OPF_MAP = {"opf": "http://www.idpf.org/2007/opf"}


def to_opf_tree(self) -> etree._Element:
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
        version="3.0",
    )

    return package


def to_opf(self, /, pretty_print: bool = False) -> str:
    return etree.tostring(
        self.to_opf_tree(),
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=pretty_print,
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
