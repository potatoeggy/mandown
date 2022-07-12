from pathlib import Path
from typing import Iterable

from .base_converter import ACCEPTED_IMAGE_EXTENSIONS, BaseConverter

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


PDF_IMAGE_MAX_INTERVAL = 200  # adjust for memory as necessary
PDF_IMAGE_MIN_INTERVAL_FACTOR = 0.12


class PdfConverter(BaseConverter):
    def create_file_progress(
        self, path: Path | str, save_to: Path | str
    ) -> Iterable[str]:
        if not HAS_PILLOW:
            raise ImportError(
                "Pillow could not be found and is required for PDF conversion"
            )

        path = Path(path)
        save_to = Path(save_to)

        images: list[Image.Image] = [
            Image.open(f)
            for f in sorted(Path.rglob(path, "*"))
            if f.suffix in ACCEPTED_IMAGE_EXTENSIONS
        ]

        if len(images) < 0:
            raise IOError("No images to convert found")

        # interval for num pdf images to process
        # at one time
        interval = round(
            min(
                PDF_IMAGE_MAX_INTERVAL,
                len(images) * PDF_IMAGE_MIN_INTERVAL_FACTOR,
            )
        )

        dest_file = save_to / (self.comic.metadata.title + ".pdf")
        for i in range(0, len(images), interval):
            append_images = (
                images[i + 1 : i + interval] if len(images) > i + 1 else None
            )
            author = (
                self.comic.metadata.authors[0] if self.comic.metadata.authors else ""
            )

            images[i].save(
                dest_file,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=append_images,
                title=self.comic.metadata.title,
                author=author,
                append=i != 0,
                creator="mandown",
                producer="mandown",
            )

            for j in images[i : i + interval]:
                j.close()
            yield "Building"


def get_class() -> type[PdfConverter]:
    return PdfConverter
