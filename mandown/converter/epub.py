import tempfile
from pathlib import Path
from typing import Iterable

from .base_converter import BaseConverter

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


class EpubConverter(BaseConverter):
    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[None]:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

    def create_skeleton(self, tmpdir: Path) -> None:
        """
        Create the following structure at `tmpdir`:
        ```
        tmpdir/
          - META-INF/container.xml
          - OEBPS/
              - Images/
              - Text/
        ```
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


def get_class() -> EpubConverter:
    return EpubConverter
