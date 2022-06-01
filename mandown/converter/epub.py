# pylint: disable=no-member

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

from lxml import etree
from lxml.builder import E, ElementMaker

from ..iohandler import NUM_LEFT_PAD_DIGITS
from .base_converter import ACCEPTED_IMAGE_EXTENSIONS, BaseConverter

STYLE_CSS = """
@page {
    margin: 0
}

body {
    display: block;
    margin: 0;
    padding: 0;
}
""".strip()

CONTAINER_XML = """
<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>
""".strip()

OPF_MAP = {"opf": "http://www.idpf.org/2007/opf"}
HTML_NS = "http://www.w3.org/1999/xhtml"


class EpubConverter(BaseConverter):
    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[None]:
        path = Path(path)
        save_to = Path(save_to)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            oebps = self.create_skeleton(root)
            self.generate_content_opf()
            self.generate_nav_xhtml()
            self.generate_toc_ncx()

            for chap in self.comic.chapters:
                yield "Building"
                for i, image in enumerate((path / chap.slug).iterdir()):
                    if image.suffix in ACCEPTED_IMAGE_EXTENSIONS:
                        new_file = (
                            oebps
                            / "Text"
                            / chap.slug
                            / f"{i:{NUM_LEFT_PAD_DIGITS}}.xhtml"
                        )
                        new_file.write_text(self.generate_image_html(chap.slug, image))

                        shutil.copyfile(
                            image,
                            oebps
                            / "Images"
                            / chap.slug
                            / f"{i:{NUM_LEFT_PAD_DIGITS}}{image.suffix}",
                        )

            dest_file = save_to / f"{self.metadata.title}.epub"
            with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as zipout:
                zipout.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
                for p in root.rglob("*"):
                    yield "Compressing"
                    if p.is_file():
                        relative_path = Path(str(p).lstrip(str(root)))
                        zipout.write(p, relative_path, zipfile.ZIP_DEFLATED)

    def create_skeleton(self, tmpdir: Path) -> Path:
        """
        Create the following structure at `tmpdir`:
        ```
        tmpdir/
          - META-INF/container.xml
          - OEBPS/
              - Images/
              - Text/
        ```
        :return The OEBPS directory.
        """
        meta_inf = tmpdir / "META-INF"
        meta_inf.mkdir()
        container_xml = meta_inf / "container.xml"
        container_xml.write_text(CONTAINER_XML, encoding="utf-8")

        oebps = tmpdir / "OEBPS"
        image_dir = oebps / "Images"
        text_dir = oebps / "Text"

        text_dir.mkdir(parents=True)
        image_dir.mkdir(parents=True)

        return oebps

    def generate_image_html(
        self,
        chapter_slug: str,
        image_path: Path,
    ) -> None:
        image_base = image_path.with_suffix("")
        tree = E.html(
            E.head(
                E.title(image_base),
                E.link(href="../style.css", type="text/css", rel="stylesheet"),
            ),
            E.body(
                E.div(style="text-align:center;top:0.0%"),
                E.img(
                    width="auto",
                    height="100%",
                    src=f"../../Images/{chapter_slug}/{image_path}",
                ),
            ),
        )

        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")

    def generate_toc_ncx(self) -> str:
        nav_map: list[etree._Element] = []

        for chap in self.comic.chapters:
            nav_map.append(
                E.navPoint(
                    E.navLabel(
                        E.text(chap.title),
                    ),
                    E.content(src=f"Text/{chap.slug}/{1:{NUM_LEFT_PAD_DIGITS}}.xhtml"),
                    id=f"Text_{chap.slug}",
                )
            )

        tree = E.ncx(
            E.head(E.meta()),
            E.docTitle(E.text(self.comic.metadata.title)),
            E.navMap(*nav_map),
        )

        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")

    def generate_content_opf(self, cover: Path | None = None) -> str:
        M = ElementMaker(  # pylint: disable=invalid-name
            namespace="http://purl.org/dc/elements/1.1/",
            nsmap=OPF_MAP,
        )

        metadata = self.comic.metadata
        els_genres = [M.subject(i) for i in metadata.genres]
        els_authors = [M.creator(i) for i in metadata.authors]

        if cover:
            cover_el = E.item(
                id="cover",
                href=f"Images/{cover.name}",
                properties="cover-image",
            )
            cover_el.attrib[
                "media-type"
            ] = f"image/{ACCEPTED_IMAGE_EXTENSIONS[cover.suffix]}"
        else:
            cover_el = None

        package = E.package(
            M.metadata(
                M.title(self.title),
                *els_authors,
                M.contributor("mandown", role="bkp"),
                M.description(metadata.description),
                M.identifier(metadata.url, scheme="URL"),
                M.language("eng"),
                *els_genres,
                M.meta(name="mandown:cover", content=self.cover_art),
                # TODO: fix cover, incorporate it in
                # TODO: also add in chapters and orientation and metas
                E.guide(E.reference(type="cover", title="Cover", href="cover")),
                nsmap=OPF_MAP["opf"],
                version="3.0",
            )
        )

        return etree.tostring(
            package,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        )

    def generate_nav_xhtml(self) -> str:
        pass


def get_class() -> EpubConverter:
    return EpubConverter
