from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from .ops import ProcessContainer

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

    if not TYPE_CHECKING:

        class Image:
            class Image:
                pass


class ProcessOps(str, Enum):
    ROTATE_DOUBLE_PAGES = "rotate_double_pages"
    """If page width is greater than its height, rotate it 90 degrees."""
    SPLIT_DOUBLE_PAGES = "split_double_pages"
    """If page width is greater than its height, split it in half into two images."""
    NO_POSTPROCESSING = "none"
    """Disable image processing entirely."""
    TRIM_BORDERS = "trim_borders"
    """Conservatively remove borders in images."""


class Processor:
    def __init__(self, image_path: Path | str) -> None:
        if not HAS_PILLOW:
            raise ImportError(
                "Pillow was not found and is needed for processing. Is it installed?"
            )

        self.image_path = Path(image_path)
        self._image = Image.open(self.image_path)
        self.is_modified = False

        # dangerous if there are multiple types of operations
        # that would add new image files to be written
        self.new_images: list[Image.Image] = []

    @property
    def image(self) -> Image.Image:
        return self._image

    @image.setter
    def image(self, image: Image.Image) -> None:
        self._image = image
        self.is_modified = True

    def write(self, filename: Path | str | None = None) -> None:
        """Save the processed image(s) manually"""
        filename = Path(filename or self.image_path)
        self.image.save(filename)

        for image in self.new_images:
            # increment by one "a" each time
            filename = filename.with_stem(filename.stem + "a")
            image.save(filename)

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
                images: tuple[Image.Image, ...] | Image.Image | None = getattr(
                    ProcessContainer, func
                )(self.image)

                if images is None:
                    continue

                if isinstance(images, Image.Image):
                    images = (images,)

                self.image = images[0]

                if len(images) > 1:
                    self.new_images.extend(images[1:])

                self.is_modified = True
            except AttributeError as err:
                raise NotImplementedError(
                    f"{func} is not a valid post-processing function."
                ) from err
            except OSError as err:
                raise OSError(f"Error in {self.image_path}") from err

        if self.is_modified:
            # only write to disk if something has actually changed
            self.write(filename)
