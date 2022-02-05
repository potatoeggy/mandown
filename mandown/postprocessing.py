from enum import Enum
from pathlib import Path

from PIL import Image


class Ops(str, Enum):
    """
    Constants for Processor.process
    """

    ROTATE_DOUBLE_PAGES = "rotate_double_pages"
    """If page width is greater than its height, rotate it 90 degrees."""
    NO_POSTPROCESSING = "none"
    """Disable image processing entirely."""


class Processor:
    def __init__(self, image_path: Path | str) -> None:
        self.image_path = Path(image_path)
        self.image = Image.open(self.image_path)

    def write(self, filename: Path | str | None = None) -> None:
        """Save the processed image manually"""
        self.image.save(filename or self.image_path)

    def process(
        self, operations: list[Ops], filename: Path | str | None = None
    ) -> None:
        """
        Perform the operations in `operations` on the image in sequence
        and save it to disk. If `filename` is not None, it will be saved
        with that filename instead.
        """
        if Ops.NO_POSTPROCESSING in operations:
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

        self.write(filename)

    def rotate_double_pages(self) -> None:
        width, height = self.image.size
        if width > height:
            self.image.rotate(90)
