# pylint: disable=no-member
"""
I'M SORRY I DON'T UNDERSTAND EPUB OKAY
"""

import shutil
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from lxml import etree
from lxml.builder import E, ElementMaker
from lxml.etree import QName

from ..io import NUM_LEFT_PAD_DIGITS, discover_local_images
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

OPF_MAP = {
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
}

NAV_MAP = {
    "epub": "http://www.idpf.org/2007/ops",
    None: "http://www.w3.org/1999/xhtml",
}


class EpubConverter(BaseConverter):
    def __post_init__(self) -> None:
        self.uuid = str(uuid4())

    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[str]:
        path = Path(path)
        save_to = Path(save_to)
        slug_map = discover_local_images(path)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            oebps = self.create_skeleton(root)
            (oebps / "toc.ncx").write_text(self.toc_ncx())
            (oebps / "nav.xhtml").write_text(self.nav_xhtml())
            (oebps / "content.opf").write_text(self.content_opf(slug_map))
            (oebps / "Text" / "style.css").write_text(STYLE_CSS)

            for chap in self.comic.chapters:
                yield "Building"

                text_dir = oebps / "Text" / chap.slug
                text_dir.mkdir(exist_ok=True)

                image_dir = oebps / "Images" / chap.slug
                image_dir.mkdir(exist_ok=True)

                for _, image in enumerate((path / chap.slug).iterdir(), start=1):
                    if image.suffix in ACCEPTED_IMAGE_EXTENSIONS:
                        new_file = text_dir / f"{image.with_suffix('').name}.xhtml"
                        new_file.write_text(self.generate_image_html(chap.slug, image))

                        shutil.copyfile(
                            image,
                            image_dir / image.name,
                        )

            dest_file = save_to / f"{self.comic.metadata.title}.epub"
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
    ) -> str:
        X = ElementMaker(  # pylint: disable=invalid-name
            namespace="http://www.w3.org/1999/xhtml",
            nsmap=NAV_MAP,
        )
        image_base = str(image_path.with_suffix(""))
        tree = X.html(
            E.head(
                E.title(image_base),
                E.link(href="../style.css", type="text/css", rel="stylesheet"),
            ),
            E.body(
                E.div(style="text-align:center;top:0.0%"),
                E.img(
                    src=f"../../Images/{chapter_slug}/{image_path.name}",
                ),
            ),
        )

        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")

    def toc_ncx(self) -> str:
        nav_map: list[etree._Element] = []

        for chap in self.comic.chapters:
            nav_map.append(
                E.navPoint(
                    E.navLabel(
                        E.text(chap.title),
                    ),
                    E.content(src=f"Text/{chap.slug}/{1:0{NUM_LEFT_PAD_DIGITS}}.xhtml"),
                    id=f"Text_{chap.slug}",
                )
            )

        tree = E.ncx(
            E.head(
                E.meta(name="dtb:uid", content=f"urn:uuid:{self.uuid}"),
                E.meta(name="dtb:depth", content="1"),
                E.meta(name="dtb:totalPageCount", content="0"),
                E.meta(name="dtb.maxPageNumber", content="0"),
                E.meta(name="generated", content="true"),
            ),
            E.docTitle(E.text(self.comic.metadata.title)),
            E.navMap(*nav_map),
            version="2005-1",
            xmlns="http://www.daisy.org/z3986/2005/ncx/",
        )
        tree.attrib[QName("http://www.w3.org/XML/1998/namespace", "lang")] = "en-US"

        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")

    def content_opf(
        self, slug_map: dict[str, list[Path]], cover: Path | None = None
    ) -> str:
        metadata = self.comic.metadata

        item_ids: list[etree._Element] = []
        item_img_ids: list[etree._Element] = [
            E.item(
                id="nav",
                href="nav.xhtml",
                properties="nav",
                **{"media-type": "application/xhtml+xml"},
            ),
            E.item(
                id="ncx", href="toc.ncx", **{"media-type": "application/x-dtbncx+xml"}
            ),
            E.item(id="css", href="Text/style.css", **{"media-type": "text/css"}),
        ]
        item_refs: list[etree._Element] = []
        for _, chap in enumerate(self.comic.chapters, start=1):
            for index, image in enumerate(slug_map[chap.slug], start=1):
                ref_id = (
                    f"page_Images_C{chap.slug}-{index:0{NUM_LEFT_PAD_DIGITS}}-mandown"
                )
                image_ref_id = (
                    f"img_Images_C{chap.slug}-{index:0{NUM_LEFT_PAD_DIGITS}}-mandown"
                )

                img_el = E.item(
                    id=image_ref_id,
                    href=f"Images/{chap.slug}/{image.name}",
                    **{
                        "media-type": f"image/{ACCEPTED_IMAGE_EXTENSIONS[image.suffix]}"
                    },
                )

                text_el = E.item(
                    id=ref_id,
                    href=f"Text/{chap.slug}/{image.with_suffix('').name}.xhtml",
                    **{"media-type": "application/xhtml+xml"},
                )

                item_ids.append(text_el)
                item_img_ids.append(img_el)
                item_refs.append(E.itemref(idref=ref_id))

        if cover:
            cover_el = E.item(
                id="cover",
                href=f"Images/{cover.name}",
                properties="cover-image",
                **{"media-type": f"image/{ACCEPTED_IMAGE_EXTENSIONS[cover.suffix]}"},
            )
            item_ids.append(cover_el)

        M = ElementMaker(  # pylint: disable=invalid-name
            # namespace="http://purl.org/dc/elements/1.1/",
            nsmap=OPF_MAP,
        )

        MD = ElementMaker(  # pylint: disable=invalid-name
            namespace="http://purl.org/dc/elements/1.1/",
            nsmap=OPF_MAP,
        )

        els_genres = [MD.subject(i) for i in metadata.genres]
        els_authors = [MD.creator(i) for i in metadata.authors]

        time_now = datetime.now().replace(microsecond=0).isoformat()

        package = E.package(
            M.metadata(
                MD.title(metadata.title),
                *els_authors,
                MD.contributor("mandown"),
                MD.description(metadata.description),
                MD.identifier(metadata.url),
                MD.identifier(f"urn:uuid:{self.uuid}", id="BookID"),
                MD.language("eng"),
                *els_genres,
                E.meta(name="mandown:cover", content=metadata.cover_art),
                E.meta(f"{time_now}Z", property="dcterms:modified"),
                # E.guide(E.reference(type="cover", title="Cover", href="cover")),
            ),
            E.manifest(*item_ids, *item_img_ids),
            E.spine(
                *item_refs,
                toc="ncx",
                **{"page-progression-direction": "ltr"},
            ),
            xmlns=OPF_MAP["opf"],
            version="3.0",
            **{"unique-identifier": "BookID"},
        )

        return etree.tostring(
            package,
            xml_declaration=False,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")

    def nav_xhtml(self) -> str:
        X = ElementMaker(  # pylint: disable=invalid-name
            namespace="http://www.w3.org/1999/xhtml",
            nsmap=NAV_MAP,
        )

        els_list: list[etree._Element] = []
        for _, chap in enumerate(self.comic.chapters, start=1):
            href = f"Text/{chap.slug}/{1:0{NUM_LEFT_PAD_DIGITS}}.xhtml"
            els_list.append(E.li(E.a(chap.title, href=href)))

        # you can't reuse elements after much head-banging
        els_list2 = deepcopy(els_list)

        tree = X.html(
            E.head(
                E.title(self.comic.metadata.title),
                E.meta(charset="utf-8"),
            ),
            E.body(
                X.nav(
                    E.ol(*els_list2),
                    id="toc",
                    **{"{http://www.idpf.org/2007/ops}type": "toc"},
                ),
                X.nav(
                    E.ol(*els_list),
                    **{"{http://www.idpf.org/2007/ops}type": "page-list"},
                ),
            ),
        )

        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        ).decode("utf-8")


def get_class() -> type[EpubConverter]:
    return EpubConverter
