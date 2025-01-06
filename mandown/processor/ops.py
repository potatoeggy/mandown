from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .profiles import SupportedProfiles, all_profiles

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

    :param `target_size`: The target size for the image. Only
    used if `resize` is enabled. Mutually exclusive with `output_profile`.
    :param `output_profile`: The output size profile to use for
    the image. Only used if `resize` is enabled. Mutually exclusive with `target_size`.
    :raises `ValueError`: If incompatible options are supplied
    :raises `KeyError`: `output_profile` is not a real key (see mandown/processor/profiles.py).
    """

    target_size: tuple[int, int] | None = None
    """
    The target size for the image. Only used if `resize`
    is enabled. Mutually exclusive with `output_profile`.
    """

    output_profile: SupportedProfiles | None = None
    """
    The output size profile to use for the image. Only
    used if `resize` is enabled. Mutually exclusive with `target_size`.
    """

    def __post_init__(self) -> None:
        if self.target_size is not None and self.output_profile is not None:
            raise ValueError("Only one of `target_size` or `output_profile` can be specified.")

        if self.output_profile is not None:
            if self.output_profile not in all_profiles:
                raise KeyError(
                    f"Invalid output profile: {self.output_profile}. See mandown."
                    "all_profiles or mandown --list-profiles for a list of valid profiles."
                )
            self.target_size = all_profiles[self.output_profile].size


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

    def split_double_pages(self, image: Image.Image) -> tuple[Image.Image, Image.Image] | None:
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


class OutputProcessContainer:
    """
    Add output processing functions here!
    Name them by their Enum string in ProcessOps.
    They should all return None.
    """

    def __init__(self, image: Image.Image, filename: str | Path) -> None:
        self.image = image
        self.filename = filename

    def default(self) -> None:
        """
        Write the image to disk.
        """
        self.image.save(self.filename)

    def webp_to_png(self) -> None:
        """
        Convert any WEBP images to PNG.
        """
        if Path(self.filename).suffix != ".webp":
            return

        path = Path(self.filename)
        self.image.save(path.with_suffix(".png"), "PNG")
        path.unlink()
