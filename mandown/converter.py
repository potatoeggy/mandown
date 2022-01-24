"""
Converts a folder of images to EPUB/PDF/CBZ/MOBI
"""
import datetime
import os
import re
import shutil
import tempfile
import textwrap
import unicodedata
from pathlib import Path
from typing import Iterator, Optional
import zipfile

from natsort import natsorted

from mandown.sources.base_source import MangaMetadata

ACCEPTED_IMAGE_EXTENSIONS = {
    ".gif": "gif",
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".jpe": "jpeg",
}


class Converter:
    def __init__(
        self,
        folder_path: str,
        metadata: Optional[MangaMetadata] = None,
        chapter_list: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        """
        Get the file path of a comic and identify its metadata.
        The chapter list is a list of tuples in the format
        (`chapter_path`, `chapter_title`), where `chapter_path`
        is the path of the chapter relative to `folder_path`.

        If the chapter list or metadata are not provided, they will
        be guessed from the directory structure.
        """
        # TODO: improve code readability
        if not Path(folder_path).is_dir():
            raise ValueError(f"{folder_path} is not a directory.")

        self.folder_path = Path(os.path.realpath(folder_path))
        self.metadata = metadata or MangaMetadata(
            title=os.path.basename(self.folder_path), authors=[], url="", cover_art=""
        )

        # self.chapters is found either by traversing the path (natsort) or by being fed
        working_chapters = chapter_list or []
        if not working_chapters:
            for item in natsorted(os.listdir(self.folder_path)):
                item = str(item)  # get rid of type complaints
                if (Path(self.folder_path) / item).is_dir():
                    working_chapters.append((item, item))

        padding = f"0{len(str(len(working_chapters)))}"

        # TODO: make cleaner this is ridiculous
        self.chapters: list[tuple[str, str, str, list[str]]] = [
            (
                title,
                sanitised,
                f"{i+1:{padding}}-{self.slugify(sanitised)}",
                list(
                    filter(
                        lambda s: any(
                            str(s).lower().endswith(i)
                            for i in ACCEPTED_IMAGE_EXTENSIONS
                        ),
                        natsorted(os.listdir(self.folder_path / sanitised)),  # type: ignore
                    )
                ),
            )
            for i, (title, sanitised) in enumerate(working_chapters)
        ]

        # useful for progress bars
        self.max_operations: dict[str, int] = {
            "epub": len(self.chapters) * 2,
            "cbz": len(self.chapters),
        }

    def to_cbz_progress(self, dest_folder: str) -> Iterator:
        dest_file = Path(dest_folder) / f"{self.metadata.title}.cbz"
        with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as file:  # type: ignore
            for dirpath, _, filenames in os.walk(self.folder_path):  # from kcc
                yield "Compressing"
                for name in filenames:
                    if (Path(dirpath) / name).is_file():
                        file.write(
                            Path(dirpath) / name,  # type: ignore
                            Path(dirpath.lstrip(str(self.folder_path))) / name,
                            zipfile.ZIP_DEFLATED,
                        )

    def to_cbz(self, dest_folder: str) -> None:
        for _ in self.to_cbz_progress(dest_folder):
            pass

    def to_epub_progress(self, dest_folder: str) -> Iterator:
        # taken from KCC generated epub file structure
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            EpubGenerator.create_skeleton(root)

            oebps = root / "OEBPS"
            with open(oebps / "Text" / "style.css", "w", encoding="utf-8") as file:
                file.write(EpubGenerator.style_css)

            with open(oebps / "content.opf", "w", encoding="utf-8") as file:
                file.write(
                    EpubGenerator.generate_content_opf(self.metadata, self.chapters)
                )

            with open(oebps / "toc.ncx", "w", encoding="utf-8") as file:
                file.write(EpubGenerator.generate_toc_ncx(self.metadata, self.chapters))

            with open(oebps / "nav.xhtml", "w", encoding="utf-8") as file:
                file.write(
                    EpubGenerator.generate_nav_xhtml(self.metadata, self.chapters)
                )

            for _, path, slug, images in self.chapters:
                yield "Building"
                os.mkdir(oebps / "Text" / slug)
                os.mkdir(oebps / "Images" / slug)
                padding = f"0{len(str(len(images)))}"

                for index, i in enumerate(images, start=1):
                    with open(
                        oebps / "Text" / slug / f"{index:{padding}}.xhtml",
                        "w",
                        encoding="utf-8",
                    ) as file:
                        file.write(
                            EpubGenerator.generate_image_html(
                                slug, f"{index:{padding}}{Path(i).suffix}"
                            )
                        )
                    shutil.copyfile(
                        self.folder_path / path / i,
                        oebps / "Images" / slug / f"{index:{padding}}{Path(i).suffix}",
                    )

            if (self.folder_path / "cover.jpg").is_file():
                shutil.copyfile(
                    self.folder_path / "cover.jpg", oebps / "Images" / "cover.jpg"
                )

            # compress and move epub
            dest_file = Path(dest_folder) / f"{self.metadata.title}.epub"

            with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as file:  # type: ignore
                file.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)  # type: ignore
                for dirpath, _, filenames in os.walk(root):  # from kcc
                    yield "Compressing"
                    for name in filenames:
                        if (Path(dirpath) / name).is_file():
                            file.write(
                                Path(dirpath) / name,  # type: ignore
                                Path(dirpath.lstrip(str(root))) / name,
                                zipfile.ZIP_DEFLATED,
                            )

    def to_epub(self, dest_folder: str) -> None:
        for _ in self.to_epub_progress(dest_folder):
            pass

    def to_pdf(self) -> None:
        pass

    def to_mobi(self) -> None:
        pass

    @staticmethod
    def slugify(string: str) -> str:
        """
        Remove all potentially invalid characters for XML
        """
        slug = unicodedata.normalize("NFKD", string)
        slug = slug.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = re.sub(r"[-]+", "-", slug)
        return slug


# pylint: disable=line-too-long
class EpubGenerator:
    style_css = textwrap.dedent(
        """\
        @page {
        margin: 0;
        }
        body {
        display: block;
        margin: 0;
        padding: 0;
        }\
        """
    )

    @staticmethod
    def create_skeleton(root: Path) -> None:
        os.mkdir(root / "META-INF")
        with open(root / "META-INF" / "container.xml", "w", encoding="utf-8") as file:
            file.write(
                textwrap.dedent(
                    """\
                    <?xml version="1.0"?>
                    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                    <rootfiles>
                    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                    </rootfiles>
                    </container>\
                    """
                )
            )

        os.mkdir(root / "OEBPS")
        os.mkdir(root / "OEBPS" / "Images")
        os.mkdir(root / "OEBPS" / "Text")

    @staticmethod
    def generate_image_html(
        chapter_slug: str, image_path: str, width: int = 1005, height: int = 1430
    ) -> str:
        image_base = Path(image_path).with_suffix("")
        return textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
            <head>
            <title>{image_base}</title>
            <link href="../style.css" type="text/css" rel="stylesheet"/>
            <meta name="viewport" content="width={width}, height={height}"/>
            </head>
            <body style="">
            <div style="text-align:center;top:0.0%;">
            <img width="{width}" height="{height}" src="../../Images/{chapter_slug}/{image_path}"/>
            </div>
            </body>
            </html>\
            """
        )

    @staticmethod
    def generate_toc_ncx(
        metadata: MangaMetadata, chapters: list[tuple[str, str, str, list[str]]]
    ) -> str:
        nav_map: list[str] = []
        for title, _, slug, images in chapters:
            padding = f"0{(len(str(len(images))))}"
            nav_map.append(
                f'<navPoint id="Text_{slug}"><navLabel><text>{title}</text></navLabel><content src="Text/{slug}/{1:{padding}}.xhtml"/></navPoint>'
            )

        return textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <ncx version="2005-1" xml:lang="en-US" xmlns="http://www.daisy.org/z3986/2005/ncx/">
            <head>
            <meta name="dtb:uid" content="urn:uuid:bafec70e-0286-49d3-b1e2-9e9f297c8cfe"/>
            <meta name="dtb:depth" content="1"/>
            <meta name="dtb:totalPageCount" content="0"/>
            <meta name="dtb:maxPageNumber" content="0"/>
            <meta name="generated" content="true"/>
            </head>
            <docTitle><text>{metadata.title}</text></docTitle>
            <navMap>
            {(chr(10) + " "*12).join(nav_map)}
            </navMap>
            </ncx>\
            """
        )

    @staticmethod
    def generate_content_opf(
        metadata: MangaMetadata, chapters: list[tuple[str, str, str, list[str]]]
    ) -> str:
        """
        `chapters` must be a list containing a tuple of elements in this order:
          - `title`, the title of the chapter
          - `sanitised_title`, the relative path to the chapter folder
          - `slug`, a safe-for-html version of the title
          - `images`, a list of paths to each image
        """

        time_now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        item_ids: list[str] = []
        item_refs: list[str] = []
        for *_, slug, images in chapters:
            padding = f"0{len(str(len(images)))}"
            for index, i in enumerate(images, start=1):
                marker = f"{index:{padding}}"
                item_ids.append(
                    f'<item id="page_Images_{slug}_{marker}" href="Text/{slug}/{marker}.xhtml" media-type="application/xhtml+xml" />'
                )
                item_ids.append(
                    f'<item id="img_Images_{slug}_{marker}" href="Images/{slug}/{marker}{Path(i).suffix}" media-type="image/{ACCEPTED_IMAGE_EXTENSIONS[Path(i).suffix]}" />'
                )

                item_refs.append(f'<itemref idref="page_Images_{slug}_{marker}" />')

        return textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <package version="3.0" unique-identifier="BookID" xmlns="http://www.idpf.org/2007/opf">
            <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:title>{metadata.title}</dc:title>
            <dc:language>en-US</dc:language>
            <dc:identifier id="BookID">urn:uuid:bafec70e-0286-49d3-b1e2-9e9f297c8cfe</dc:identifier>
            <dc:contributor id="contributor">mandown</dc:contributor>
            {(chr(10) + " "*12).join(
                f'<dc:creator id="id-{i}">{name}</dc:creator>'
                for i, name in enumerate(metadata.authors)
            )}
            <meta property="dcterms:modified">{time_now}Z</meta>
            <meta name="cover" content="cover"/>
            <meta property="rendition:orientation">portrait</meta>
            <meta property="rendition:spread">both</meta>
            <meta property="rendition:layout">pre-paginated</meta>
            </metadata>
            <manifest>
            <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
            <item id="nav" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/>
            <item id="css" href="Text/style.css" media-type="text/css"/>
            <item id="cover" href="Images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
            {(chr(10) + " "*12).join(item_ids)}
            </manifest>
            <spine page-progression-direction="ltr" toc="ncx">
            {(chr(10) + " "*12).join(item_refs)}
            </spine>
            </package>\
            """
        )

    @staticmethod
    def generate_nav_xhtml(
        metadata: MangaMetadata, chapters: list[tuple[str, str, str, list[str]]]
    ) -> str:
        lis: list[str] = []
        for title, _, slug, images in chapters:
            padding = f"0{len(str(len(images)))}"
            lis.append(
                f'<li><a href="Text/{slug}/{1:{padding}}.xhtml">{title}</a></li>'
            )

        return textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="utf-8"?>
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
            <head>
            <title>{metadata.title}</title>
            <meta charset="utf-8"/>
            </head>
            <body>
            <nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc">
            <ol>
            {(chr(10) + " "*12).join(lis)}
            </ol>
            </nav>
            <nav epub:type="page-list">
            <ol>
            {(chr(10) + " "*12).join(lis)}
            </ol>
            </nav>
            </body>
            </html>\
            """
        )
