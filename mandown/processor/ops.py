from typing import TYPE_CHECKING

try:
    from PIL import Image, ImageChops
except ImportError:

    if not TYPE_CHECKING:

        class Image:
            class Image:
                pass

        class ImageChops:
            pass


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

    @staticmethod
    def rotate_double_pages(image: Image.Image) -> Image.Image | None:
        width, height = image.size
        if width > height:
            return image.rotate(90, expand=1)
        return None

    @staticmethod
    def split_double_pages(
        image: Image.Image,
    ) -> tuple[Image.Image, Image.Image] | None:
        width, height = image.size
        if not width > height:
            return None

        left = image.crop((0, 0, int(width / 2), height))
        right = image.crop((int(width / 2), 0, width, height))
        return (left, right)

    @staticmethod
    def trim_borders(image: Image.Image) -> Image.Image | None:
        bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
        diff = ImageChops.difference(image, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return image.crop(bbox)
        return None
