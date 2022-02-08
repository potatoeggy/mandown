import multiprocessing as mp
from enum import Enum
from pathlib import Path
from typing import Iterable

from PIL import Image


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


class Processor:
    def __init__(self, image_path: Path | str, right_to_left: bool = False) -> None:
        self.image_path = Path(image_path)
        self.image = Image.open(self.image_path)
        self.modified = False
        self.right_to_left = right_to_left

        self.pending_images: list[tuple[Image.Image, Path]] = []

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
            self.modified = True

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


def async_process(data: tuple[Path | str, list[ProcessOps]]) -> None:
    image_path, ops = data
    processor = Processor(image_path)
    processor.process(ops)


def process_progress(
    folder_paths: list[Path], options: list[ProcessOps], maxthreads: int = 4
) -> Iterable[None]:
    map_pool: list[tuple[Path | str, list[ProcessOps]]] = []
    for folder in folder_paths:
        for image_path in folder.iterdir():
            if image_path.is_file():
                map_pool.append((image_path.absolute(), options))

    with mp.Pool(maxthreads) as pool:
        yield from pool.imap_unordered(async_process, map_pool)


def process(
    folder_paths: list[Path], options: list[ProcessOps], maxthreads: int = 4
) -> None:
    for _ in process_progress(folder_paths, options, maxthreads):
        pass
