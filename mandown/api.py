from pathlib import Path
from typing import Iterable

from mandown.processor import ProcessOps, Processor

from . import iohandler, sources
from .comic import BaseComic
from .converter import ConvertFormats, get_converter


def query(url: str) -> BaseComic:
    """
    Attempt to query for a comic given a URL.
    :param `url`: An internet URL to search for
    """
    adapter = sources.get_class_for(url)(url)
    return BaseComic(adapter.metadata, adapter.chapters)


def read(path: Path | str) -> BaseComic:
    """
    Load a mandown-created comic from the file system.
    :param `path`: A folder where mandown has created a comic
    :throws FileNotFoundError if `md-metadata.json` cannot be found.
    """
    return iohandler.read_comic(path)


def convert_progress(
    comic: BaseComic,
    folder_path: Path | str,
    convert_to: ConvertFormats,
    dest_folder: Path | str | None = None,
) -> Iterable:
    if convert_to == ConvertFormats.NONE:
        return

    # default to working directory
    dest_folder = dest_folder or Path(".").resolve()

    # obviously pylint is wrong because this is 100% callable
    converter = get_converter(convert_to)(comic)  # pylint: disable=not-callable
    yield from converter.create_file_progress(folder_path, dest_folder)


def convert(
    comic: BaseComic,
    folder_path: Path | str,
    convert_to: ConvertFormats,
    dest_folder: Path | str | None = None,
) -> None:
    for _ in convert_progress(comic, folder_path, convert_to, dest_folder):
        pass


def process_progress(
    comic_path: Path | str, ops: list[ProcessOps] | None = None
) -> Iterable:
    data = iohandler.discover_local_images(comic_path)
    for _, images in data.items():
        for i in images:
            Processor(i).process(ops)
        yield "1 chapter"


def process(comic: BaseComic, ops: list[ProcessOps] | None = None) -> None:
    for _ in process_progress(comic, ops):
        pass


def download_progress(
    comic: BaseComic,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 2,
    only_download_missing: bool = True,
) -> Iterable:
    path = Path(path)

    # create dir
    try:
        full_path = path / comic.metadata.title
        full_path.mkdir(exist_ok=True)
    except IOError:
        # invalid filename
        full_path = path / comic.metadata.title_slug
        full_path.mkdir(exist_ok=True)

    # save metadata json
    comic.set_chapter_range(start=start, end=end)
    iohandler.save_comic(comic, full_path)

    # cover
    if comic.metadata.cover_art:
        next(
            iohandler.download_images(
                [comic.metadata.cover_art], full_path, filestems=["cover"]
            )
        )

    # for each chapter
    for chap in comic.chapters[start:end]:
        image_urls = comic.get_chapter_image_urls(chap)
        # expect that they're named by numbers only
        skip_images: set[int] = set()
        if only_download_missing:
            for file in path.iterdir():
                if file.stem == file.stem.rjust(iohandler.NUM_LEFT_PAD_DIGITS, "0"):
                    try:
                        skip_images.add(int(file.stem))
                    except ValueError:
                        # expected if not an image file
                        pass

        if not image_urls or len(skip_images) == len(image_urls):
            # skip processing if there's nothing to download
            continue

        # name them 00001.png, 00002.png, etc
        # skipping ones that already exist
        processed_image_urls, filestems = zip(
            *(
                (link, str(i).rjust(iohandler.NUM_LEFT_PAD_DIGITS, "0"))
                for i, link in enumerate(image_urls, start=1)
                if i not in skip_images
            )
        )

        chapter_path = full_path / chap.slug

        for _ in iohandler.download_images(
            processed_image_urls,
            chapter_path,
            headers=comic.source.headers,
            filestems=filestems,
            threads=threads,
        ):
            pass
        yield


def download(
    comic: BaseComic,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 2,
    only_download_missing: bool = True,
) -> None:
    for _ in download_progress(
        comic,
        path,
        start=start,
        end=end,
        threads=threads,
        only_download_missing=only_download_missing,
    ):
        pass
