# pylint: disable=invalid-name

import shutil
from pathlib import Path
from typing import Iterator

import comicon

from . import io, sources
from .comic import BaseComic
from .convert_utils import ConvertFormats, convert_one
from .errors import ChapterImageCountMismatchError, ImageDownloadError
from .processor import ProcessConfig, ProcessOps, Processor


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

    :raises FileNotFoundError if `md-metadata.json` cannot be found
    :raises IOError if the path does not exist
    """
    return io.read_comic(path)


def save_metadata(comic: BaseComic, path: Path | str) -> None:
    """
    Save the metadata from the comic to `<path>/md-metadata.json`.

    :param `comic`: A comic with metadata to save
    :param `path`: A folder to save the metadata to
    """
    io.save_comic(comic, path)


def init_parse_comic(
    path: Path | str, donor_comic: BaseComic | None = None, download_cover: bool = False
) -> BaseComic:
    """
    Open a comic from a folder path, either via `md-metadata.json` or
    if that fails, parse the comic structure and create an `md-metadata.json`

    :param `path`: A folder containing `md-metadata.json` or a comic structure
    :param `data`: A comic to fill metadata from if no metadata is found
    :param `download_cover`: If `True` and `source_url` is set, download
    the cover image if no metadata is found
    :returns A comic with metadata and chapter data of that folder
    :raises `AttributeError` if the source URL is not set and `download_cover` is `True`
    """
    if not donor_comic and download_cover:
        raise AttributeError("Cannot download cover without donor comic")

    try:
        comic = io.read_comic(path)
    except FileNotFoundError:
        comic = io.parse_comic(path, donor_comic)
        io.save_comic(comic, path)

        if download_cover and comic.metadata.cover_art:
            next(
                io.download_images(
                    [comic.metadata.cover_art],
                    path,
                    filestems=["cover"],
                    headers=comic.source.headers,
                )
            )
    return comic


def convert_progress(
    comic_path: Path | str,
    to: ConvertFormats,
    dest_folder: Path | str | None = None,
    remove_after: bool = False,
    split_by_chapters: bool = False,
) -> Iterator[str | int]:
    """
    Convert the comic located at `folder_path` to `convert_to`
    and put it in `dest_folder` (defaults to workdir).

    :param `comic_path`: The path to the comic to convert (may be in Mandown
    folder form or any of the `mandown.ConvertFormats` such as EPUB)
    :param `convert_to`: The format to convert to
    :param `dest_folder`: A folder to put the converted comic in
    :param `remove_after`: If `True`, delete the original file/folder after conversion
    :param `split_by_chapters`: Only applies to Mandown-created comics. If `True`,
    output a comic file per chapter. Existing comic files will not be overwritten.

    :returns An `Iterator` representing a progress bar. The first iteration returns
    the remaining number of iterations. If converting between file formats, an
    iteration after the first number of iterations ends will return the remaining
    number of the second number of iterations.
    """
    comic_path = Path(comic_path)
    if to == ConvertFormats.NONE:
        return

    # default to working directory
    dest_folder = Path(dest_folder or ".").resolve()

    if comic_path.is_dir():
        # it's a mandown comic, convert it to CIR
        comic = load(comic_path)

        # find cover
        cover: str | None = None
        for item in comic_path.iterdir():
            if item.name.startswith("cover"):
                cover = item.name
                break

        if split_by_chapters:
            comicon_comics = [
                comicon.Comic(
                    comicon.Metadata(
                        title=f"{comic.metadata.title} - {chap.title}",
                        authors=comic.metadata.authors,
                        description=comic.metadata.description,
                        genres=comic.metadata.genres,
                        cover_path_rel=cover,
                    ),
                    [comicon.Chapter(chap.title, chap.slug)],
                )
                for chap in comic.chapters
            ]

            yield len(comicon_comics)
            existing_filenames = {file.name for file in dest_folder.iterdir() if file.is_file()}
            for comicomic in comicon_comics:
                yield comicomic.metadata.title

                # do not overwrite existing cache
                if f"{comicomic.metadata.title_slug}.{to.value}" in existing_filenames:
                    continue
                for _ in convert_one(comicomic, comic_path, to, dest_folder):
                    ...

        else:
            comicon_comic = comicon.Comic(
                comicon.Metadata(
                    title=comic.metadata.title,
                    authors=comic.metadata.authors,
                    description=comic.metadata.description,
                    genres=comic.metadata.genres,
                    cover_path_rel=cover,
                ),
                [comicon.Chapter(chap.title, chap.slug) for chap in comic.chapters],
            )

            yield from convert_one(comicon_comic, comic_path, to, dest_folder)

    else:
        # it's a file, no conversion needed, let comicon do its inferencing
        yield from comicon.convert_progress(
            comic_path, dest_folder / f"{comic_path.stem}.{to.value}"
        )

    if remove_after:
        shutil.rmtree(comic_path)


def convert(
    comic_path: Path | str,
    to: ConvertFormats,
    dest_folder: Path | str | None = None,
    remove_after: bool = False,
) -> None:
    """
    Convert the comic located at `folder_path` to `convert_to`
    and put it in `dest_folder` (defaults to workdir).

    :param `comic_path`: The path to the comic to convert (may be in Mandown
    folder form or any of the `mandown.ConvertFormats` such as EPUB)
    :param `convert_to`: The format to convert to
    :param `dest_folder`: A folder to put the converted comic in
    :param `remove_after`: If `True`, delete the original file/folder after conversion
    """
    for _ in convert_progress(comic_path, to, dest_folder, remove_after):
        pass


def process_progress(
    comic_path: Path | str, ops: list[ProcessOps], config: ProcessConfig | None = None
) -> Iterator[str]:
    """
    Process the comic in `comic_path` with `ops` in the order provided.

    :param `comic_path`: A folder containing a image folders to process
    :param `ops`: A list of operations to perform on each image
    :param `config`: Options for processing operations
    :returns An `Iterator` representing a progress bar up to the number of images in the comic.
    """
    data = io.discover_local_images(comic_path)
    for _, images in data.items():
        for i in images:
            Processor(i, config).process(ops)
        yield "Processing"


def process(
    comic_path: Path | str, ops: list[ProcessOps], config: ProcessConfig | None = None
) -> None:
    """
    Process the comic in `comic_path` with `ops` in the order provided.

    :param `comic_path`: A folder containing a image folders to process
    :param `ops`: A list of operations to perform on each image
    :param `config`: Options for processing operations
    """
    for _ in process_progress(comic_path, ops, config):
        pass


def download_progress(
    comic: BaseComic | str,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 4,
    only_download_missing: bool = True,
    raise_on_failed_download: bool = True,
) -> Iterator[str]:
    """
    Download comic or comic URL `comic` to `path` using `threads` threads.

    :param `comic`: A comic or URL to download
    :param `path`: A folder to download the comic to
    :param `start`: The first chapter to download (zero-indexed, inclusive)
    :param `end`: The last chapter to download (zero-indexed, exclusive)
    :param `threads`: The number of threads to use
    :param `only_download_missing`: If `True`, do not download
    images already in the destination path

    :returns An `Iterator` representing a progress bar up to the number of chapters in the comic.
    """
    path = Path(path)

    # make var comic a BaseComic
    if isinstance(comic, str):
        comic = query(comic)

    full_path = path / comic.metadata.title_slug
    full_path.mkdir(exist_ok=True)

    # save metadata json
    comic.set_chapter_range(start=start, end=end)
    io.save_comic(comic, full_path)

    # cover
    if comic.metadata.cover_art:
        for _ in io.download_images(
            [comic.metadata.cover_art],
            full_path,
            filestems=["cover"],
            headers=comic.source.headers,
        ):
            pass

    # for each chapter
    for chap in comic.chapters[start:end]:
        yield chap.title
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
            continue

        # name them 00001.png, 00002.png, etc
        # skipping ones that already exist
        try:
            processed_image_urls, filestems = zip(
                *(
                    (link, str(i).rjust(io.NUM_LEFT_PAD_DIGITS, "0"))
                    for i, link in enumerate(image_urls, start=1)
                    if i not in skip_images
                ),
                strict=False,
            )
        except ValueError:
            # ValueError is raised when `zip` is given no arguments and thus
            # no images to download
            processed_image_urls, filestems = [], []

            raise ChapterImageCountMismatchError(
                "There are more images in the filesystem than in present in the chapter index."
                " You should never see this message."
            ) from None

        chapter_path = full_path / chap.slug

        for _ in io.download_images(
            processed_image_urls,
            chapter_path,
            headers=comic.source.headers,
            filestems=filestems,
            threads=threads,
        ):
            pass

        # check if every image was downloaded
        if count := len([f for f in chapter_path.iterdir() if f.is_file()]) != len(
            processed_image_urls
        ):
            if raise_on_failed_download:
                raise ImageDownloadError(
                    f"Failed to download {len(processed_image_urls) - count} images"
                )


def download(
    comic: BaseComic | str,
    path: Path | str = ".",
    *,
    start: int | None = None,
    end: int | None = None,
    threads: int = 4,
    only_download_missing: bool = True,
    raise_on_failed_download: bool = True,
) -> None:
    """
    Download comic or comic URL `comic` to `path` using `threads` threads.

    :param `comic`: A comic or URL to download
    :param `path`: A folder to download the comic to
    :param `start`: The first chapter to download (one-indexed, inclusive)
    :param `end`: The last chapter to download (one-indexed, inclusive)
    :param `threads`: The number of threads to use
    :param `only_download_missing`: If `True`, do not download images
    already in the destination path
    """
    for _ in download_progress(
        comic,
        path,
        start=start,
        end=end,
        threads=threads,
        only_download_missing=only_download_missing,
        raise_on_failed_download=raise_on_failed_download,
    ):
        pass
