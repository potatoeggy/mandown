from dataclasses import dataclass
from typing import TYPE_CHECKING

try:
    from PIL import Image, ImageChops

    if not hasattr(Image, "Resampling"):  # Pillow<9.0
        Image.Resampling = Image
except ImportError:

    if not TYPE_CHECKING:

        class Image:
            class Image:
                pass

        class ImageChops:
            pass


@dataclass(kw_only=True, slots=True)
class ProcessConfig:
    """
    A class for storing configuration for processing images.

    :param `target_size`: The target size for the image. Only used if `resize` is enabled.
    """

    target_size: tuple[int, int] | None = None
    """The target size for the image. Only used if `resize` is enabled."""


class ProcessContainer:
    """
    Add processing functions here!
    Name them by their Enum string in ProcessOps.
    They should all return a Image.Image | tuple[Image.Image] | None
    depending on if they can return multiple images.

    The first image returned will replace the current image,
    all other ones will be suffixed with `a`. If `None` is returned,
    the image will not be altered.
    """

    def __init__(self, config: ProcessConfig | None = None):
        self.config = config or ProcessConfig()

    def rotate_double_pages(
        self,
        image: Image.Image,
    ) -> Image.Image | None:
        """
        Rotate the image 90 degrees if it is a double page so it fits on the screen.
        """
        width, height = image.size
        if width > height:
            return image.rotate(90, expand=1)
        return None

    def split_double_pages(
        self, image: Image.Image
    ) -> tuple[Image.Image, Image.Image] | None:
        """
        Split the image into two separate images if it is a double page.
        """
        width, height = image.size
        if not width > height:
            return None

        left = image.crop((0, 0, int(width / 2), height))
        right = image.crop((int(width / 2), 0, width, height))
        return (left, right)

    def trim_borders(self, image: Image.Image) -> Image.Image | None:
        """
        Trim the borders of the image.
        """
        bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
        diff = ImageChops.difference(image, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return image.crop(bbox)
        return None

    def resize(
        self,
        image: Image.Image,
    ) -> Image.Image | None:
        """
        Resize the image to a maximum width and height.
        """
        target_size = self.config.target_size

        if target_size is None or image.size == target_size:
            return None
        return image.resize(target_size, resample=Image.Resampling.LANCZOS)
