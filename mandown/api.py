import shutil
from pathlib import Path
from typing import Iterator

from . import io, sources
from .comic import BaseComic
from .converter import ConvertFormats, get_converter
from .processor import ProcessOps, Processor


def query(url: str) -> BaseComic:
    """
    Attempt to query for a comic given a URL.
    :param `url`: An internet URL to search for
    :raises `ValueError` if the source is not found.
    """
    adapter = sources.get_class_for(url)(url)
    return BaseComic(adapter.metadata, adapter.chapters)


def load(path: Path | str) -> BaseComic:
    """
    Load a mandown-created comic from the file system.

    :param `path`: A folder where mandown has created a comic
    :returns A comic with metadata and chapter data of that folder

    :throws FileNotFoundError if `md-metadata.json` cannot be found.
    """
    return io.read_comic(path)


def save_metadata(comic: BaseComic, path: Path | str) -> None:
    """
    Save the metadata from the comic to `<path>/md-metadata.json`.

    :param `comic`: A comic with metadata to save
    :param `path`: A folder to save the metadata to
    """
    io.save_comic(comic, path)


def init_parse_comic(path: Path | str, source_url: str | None = None) -> BaseComic:
    """
    Open a comic from a folder path, either via `md-metadata.json` or
    if that fails, parse the comic structure and create an `md-metadata.json`

    :param `path`: A folder containing `md-metadata.json` or a comic structure
    :param `source_url`: A source URL to fill metadata from
    :returns A comic with metadata and chapter data of that folder
    """
    try:
        comic = io.read_comic(path)
    except FileNotFoundError:
        comic = io.parse_comic(path, source_url)
        io.save_comic(comic, path)
    return comic


def convert_progress(
    comic: BaseComic,
    folder_path: Path | str,
    convert_to: ConvertFormats,
    dest_folder: Path | str | None = None,
    remove_after: bool = False,
) -> Iterator[str]:
    """
    From metadata in `comic`, convert the comic in `folder_path`
    to `convert_to` and put it in `dest_folder` (defaults to workdir).

    :param `comic`: A comic with metadata to convert
    :param `folder_path`: A folder containing the comic to convert
    :param `convert_to`: The format to convert to
    :param `dest_folder`: A folder to put the converted comic in
    :param `remove_after`: If `True`, delete the original folder after conversion

    :returns An `Iterator` representing a progress bar up to the number of chapters in the comic.
    """
    if convert_to == ConvertFormats.NONE:
        return

    # default to working directory
    dest_folder = dest_folder or Path(".").resolve()

    # obviously pylint is wrong because this is 100% callable
    converter = get_converter(convert_to)(comic)  # pylint: disable=not-callable
    yield from converter.create_file_progress(folder_path, dest_folder)

    if remove_after:
        shutil.rmtree(folder_path)


def convert(
    comic: BaseComic,
    folder_path: Path | str,
    convert_to: ConvertFormats,
    dest_folder: Path | str | None = None,
    remove_after: bool = False,
) -> None:
    """
    From metadata in `comic`, convert the comic in `folder_path`
    to `convert_to` and put it in `dest_folder` (defaults to workdir).

    :param `comic`: A comic with metadata to convert
    :param `folder_path`: A folder containing the comic to convert
    :param `convert_to`: The format to convert to
    :param `dest_folder`: A folder to put the converted comic in
    :param `remove_after`: If `True`, delete the original folder after conversion
    """
    for _ in convert_progress(
        comic, folder_path, convert_to, dest_folder, remove_after
    ):
        pass


def process_progress(comic_path: Path | str, ops: list[ProcessOps]) -> Iterator[str]:
    """
    Process the comic in `comic_path` with `ops` in the order provided.

    :param `comic_path`: A folder containing a image folders to process
    :param `ops`: A list of operations to perform on each image
    :returns An `Iterator` representing a progress bar up to the number of images in the comic.
    """
    data = io.discover_local_images(comic_path)
    for _, images in data.items():
        for i in images:
            Processor(i).process(ops)
        yield "Processing"


def process(comic_path: Path | str, ops: list[ProcessOps]) -> None:
    """
    Process the comic in `comic_path` with `ops` in the order provided.

    :param `comic_path`: A folder containing a image folders to process
    :param `ops`: A list of operations to perform on each image
    :returns An `Iterator` representing a progress bar up to the number of images in the comic.
    """
    for _ in process_progress(comic_path, ops):
        pass


def download_progress(
    comic: BaseComic | str,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 4,
    only_download_missing: bool = True,
) -> Iterator[str]:
    """
    Download comic or comic URL `comic` to `path` using `threads` threads.

    :param `comic`: A comic or URL to download
    :param `path`: A folder to download the comic to
    :param `start`: The first chapter to download (one-indexed, inclusive)
    :param `end`: The last chapter to download (one-indexed, inclusive)
    :param `threads`: The number of threads to use
    :param `only_download_missing`: If `True`, do not download images already in the destination path

    :returns An `Iterator` representing a progress bar up to the number of chapters in the comic.
    """
    path = Path(path)

    # make var comic a BaseComic
    if isinstance(comic, str):
        comic = query(comic)

    # create dir
    try:
        full_path = path / comic.metadata.title
    except IOError:
        # invalid filename
        full_path = path / comic.metadata.title_slug
    full_path.mkdir(exist_ok=True)

    # save metadata json
    comic.set_chapter_range(start=start, end=end)
    io.save_comic(comic, full_path)

    # cover
    if comic.metadata.cover_art:
        for _ in io.download_images(
            [comic.metadata.cover_art], full_path, filestems=["cover"]
        ):
            pass

    # for each chapter
    for chap in comic.chapters[start:end]:
        image_urls = comic.get_chapter_image_urls(chap)
        chapter_path = full_path / chap.slug
        chapter_path.mkdir(exist_ok=True)

        # expect that they're named by numbers only
        skip_images: set[int] = set()
        if only_download_missing:
            for file in chapter_path.iterdir():
                if file.stem == file.stem.rjust(io.NUM_LEFT_PAD_DIGITS, "0"):
                    try:
                        skip_images.add(int(file.stem))
                    except ValueError:
                        # expected if not an image file
                        pass

        if not image_urls or len(skip_images) == len(image_urls):
            # move to next chapter if there's nothing to download for this one
            yield chap.title
            continue

        # name them 00001.png, 00002.png, etc
        # skipping ones that already exist
        processed_image_urls, filestems = zip(
            *(
                (link, str(i).rjust(io.NUM_LEFT_PAD_DIGITS, "0"))
                for i, link in enumerate(image_urls, start=1)
                if i not in skip_images
            )
        )

        chapter_path = full_path / chap.slug

        for _ in io.download_images(
            processed_image_urls,
            chapter_path,
            headers=comic.source.headers,
            filestems=filestems,
            threads=threads,
        ):
            pass
        yield chap.title


def download(
    comic: BaseComic | str,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 4,
    only_download_missing: bool = True,
) -> None:
    """
    Download comic or comic URL `comic` to `path` using `threads` threads.

    :param `comic`: A comic or URL to download
    :param `path`: A folder to download the comic to
    :param `start`: The first chapter to download (one-indexed, inclusive)
    :param `end`: The last chapter to download (one-indexed, inclusive)
    :param `threads`: The number of threads to use
    :param `only_download_missing`: If `True`, do not download images already in the destination path
    """
    for _ in download_progress(
        comic,
        path,
        start=start,
        end=end,
        threads=threads,
        only_download_missing=only_download_missing,
    ):
        pass
