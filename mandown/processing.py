from enum import Enum
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageChops

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class ProcessOps(str, Enum):
    """
    Constants for Processor.process
    """

    ROTATE_DOUBLE_PAGES = "rotate_double_pages"
    """If page width is greater than its height, rotate it 90 degrees."""
    SPLIT_DOUBLE_PAGES = "split_double_pages"
    """If page width is greater than its height, split it in half into two images."""
    NO_POSTPROCESSING = "none"
    """Disable image processing entirely."""
    TRIM_BORDERS = "trim_borders"
    """Conservatively remove borders in images."""


class Processor:
    def __init__(self, image_path: Path | str, right_to_left: bool = False) -> None:
        if not HAS_PILLOW:
            raise ImportError(
                "Pillow was not found and is needed for processing. Is it installed?"
            )
        self.image_path = Path(image_path)
        self._image = Image.open(self.image_path)
        self.modified = False
        self.right_to_left = right_to_left

        # what if we need to process pending images in future operations?
        self.pending_images: list[tuple[Image.Image, Path]] = []

    @property
    def image(self) -> Image.Image:
        return self._image

    @image.setter
    def image(self, image: Image.Image) -> None:
        self._image = image
        self.modified = True

    def write(self, filename: Path | str | None = None) -> None:
        """Save the processed image manually"""
        self.image.save(filename or self.image_path)

        for image, path in self.pending_images:
            image.save(path)

    def process(
        self, operations: list[ProcessOps], filename: Path | str | None = None
    ) -> None:
        """
        Perform the operations in `operations` on the image in sequence
        and save it to disk. If `filename` is not None, it will be saved
        with that filename instead.
        """
        if ProcessOps.NO_POSTPROCESSING in operations:
            return

        for func in operations:
            try:
                getattr(self, func)()
            except AttributeError as err:
                raise NotImplementedError(
                    f"{func} is not a valid post-processing function."
                ) from err
            except OSError as err:
                raise OSError(f"Error in {self.image_path}") from err

        if self.modified:
            # only write to disk if something has actually changed
            self.write(filename)

    def rotate_double_pages(self) -> None:
        width, height = self.image.size
        if width > height:
            self.image = self.image.rotate(90, expand=1)

    def split_double_pages(self) -> None:
        width, height = self.image.size
        if not width > height:
            return

        left = self.image.crop((0, 0, int(width / 2), height))
        right = self.image.crop((int(width / 2), 0, width, height))

        self.image = right if self.right_to_left else left
        new_image = left if self.right_to_left else right

        new_image_path = self.image_path.with_stem(self.image_path.stem + ".5")
        self.pending_images.append((new_image, new_image_path))

    def trim_borders(self) -> None:
        bg = Image.new(self.image.mode, self.image.size, self.image.getpixel((0, 0)))
        diff = ImageChops.difference(self.image, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            self.image = self.image.crop(bbox)


def async_process(data: tuple[Path | str, list[ProcessOps]]) -> None:
    image_path, ops = data
    processor = Processor(image_path)
    processor.process(ops)
