from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from .ops import OutputProcessContainer, ProcessConfig, ProcessContainer

try:
    from PIL import Image, ImageFile

    ImageFile.LOAD_TRUNCATED_IMAGES = True

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

    RESIZE = "resize"
    """Resize images to a maximum width and height."""

    WEBP_TO_PNG = "webp_to_png"
    """Convert any WEBP images to PNG."""


"""A list of operations that can be chained."""
IN_MEM_PROCESS_OPS = {
    ProcessOps.ROTATE_DOUBLE_PAGES,
    ProcessOps.SPLIT_DOUBLE_PAGES,
    ProcessOps.TRIM_BORDERS,
    ProcessOps.RESIZE,
}

"""A list of operations that must be run last."""
OUTPUT_PROCESS_OPS = {
    ProcessOps.WEBP_TO_PNG,
}


class ProcessOptionMismatchError(Exception):
    """Raised when an option is not valid for a given operation or
    there are missing options."""


class Processor(ProcessContainer):
    """
    A class for processing images.

    :param `image_path`: The path to the image to process
    :raises `ImportError`: If Pillow is not installed
    :raises `ProcessOptionMismatchError`: If an option is not valid for
    a given operation or there are missing options
    """

    def __init__(self, image_path: Path | str, config: ProcessConfig | None = None) -> None:
        if not HAS_PILLOW:
            raise ImportError("Pillow was not found and is needed for processing. Is it installed?")

        super().__init__(config)
        self.image_path = Path(image_path)
        self._image = Image.open(self.image_path)
        self.is_modified = False

        # WARN: dangerous if there are multiple types of operations
        # that would add new image files to be written
        self.new_images: list[Image.Image] = []

    @property
    def image(self) -> Image.Image:
        """
        The image to process. This is a `PIL.Image.Image` object.

        :setter: Set the image to process
        :returns: The image to process
        """
        return self._image

    @image.setter
    def image(self, image: Image.Image) -> None:
        self._image = image
        self.is_modified = True

    def write(
        self, filename: Path | str | None = None, output_process_op: ProcessOps | None = None
    ) -> None:
        """Save the processed image(s) manually"""
        filename = Path(filename or self.image_path)

        writer = OutputProcessContainer(self.image, filename)
        getattr(writer, output_process_op or "default")()  # this is so janky

        for image in self.new_images:
            # increment by one "a" each time
            filename = filename.with_stem(filename.stem + "a")
            writer = OutputProcessContainer(image, filename)
            getattr(writer, output_process_op or "default")()

    def process(self, operations: list[ProcessOps], filename: Path | str | None = None) -> None:
        """
        Perform the operations in `operations` on the image in sequence
        and save it to disk. If `filename` is not None, it will be saved
        with that filename instead. If "none" is in `operations`, no
        post-processing will be done.

        :param operations: A list of operations to perform on the image
        :param filename: The filename to save the image as
        :raises NotImplementedError: If an operation is not implemented
        :raises OSError: If there is an error in saving the image
        :raises ProcessOptionMismatchError: If an option is not valid for a
        given operation or there are missing options
        """
        if ProcessOps.NO_POSTPROCESSING in operations:
            return

        # TODO: move all the checks together
        # there are some in ProcessConfig rn
        resize_op_valid = bool(self.config.output_profile or self.config.target_size) ^ bool(
            ProcessOps.RESIZE in operations
        )
        if resize_op_valid:
            # if any of the following is true:
            # - target_size is set and resize is not
            # - profile is set and resize is not
            # - resize is set and neither target_size nor profile is set
            # testing if only one of them is set is done in the resize op itself
            raise ProcessOptionMismatchError("resize must be used with target_size or profile")

        output_op: ProcessOps | None = None

        for func in operations:
            if func in OUTPUT_PROCESS_OPS:
                if output_op:
                    # only one output operation can be run
                    raise ProcessOptionMismatchError(
                        "Only one output operation can be run."
                        f"{output_op} and {func} were both found."
                    )
                output_op = func
                continue

            try:
                images: tuple[Image.Image, ...] | Image.Image | None = getattr(self, func)(
                    self.image
                )

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

        if self.is_modified or output_op:
            # only write to disk if something has actually changed
            self.write(filename, output_op)
