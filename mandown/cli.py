#!/usr/bin/env python3

import importlib.metadata
import os
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, List, Optional

import requests
import typer

import mandown
from mandown.converter import Converter
from mandown.processing import ProcessOps
from mandown.sources.base_source import BaseSource, Chapter, MangaMetadata

app = typer.Typer()


class ConvertFormats(str, Enum):
    CBZ = "cbz"
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"
    FOLDER = "folder"


# helper functions to repeat less code
def cli_query(url: str) -> BaseSource | None:
    typer.echo(f"Searching sources for {url}")
    try:
        source: BaseSource = mandown.query(url, populate=True)
        typer.secho(f'Found item from source "{source.name}"', fg=typer.colors.GREEN)
        typer.secho(source)
    except ValueError as err:
        typer.secho("Could not match URL with available sources.", fg=typer.colors.RED)
        raise typer.Exit(1) from err

    return source


def cli_convert(
    folder_path: str,
    target_format: ConvertFormats,
    dest: Path = Path(os.getcwd()),
    metadata: MangaMetadata | None = None,
    chapter_list: list[tuple[str, str]] | None = None,
) -> None:
    converter = Converter(folder_path, metadata, chapter_list)
    convert_func: Callable[[str], Iterable] = lambda i: None
    match target_format:
        case ConvertFormats.EPUB:
            convert_func = converter.to_epub_progress
        case ConvertFormats.CBZ:
            convert_func = converter.to_cbz_progress
        case ConvertFormats.PDF:
            convert_func = converter.to_pdf_progress
        case _:
            raise NotImplementedError(
                f"{target_format} conversion has not been implemented yet!"
            )
    with typer.progressbar(
        convert_func(dest),
        length=converter.max_operations[target_format.value],
        label="Converting",
    ) as progress:
        for _ in progress:
            pass

    dest_file = (dest / Path(folder_path).stem).with_suffix(f".{target_format.value}")
    typer.secho(f"Successfully converted to {dest_file}", fg=typer.colors.GREEN)


def cli_process(
    folder_paths: list[Path], options: list[ProcessOps], maxthreads: int = 4
) -> None:
    # only goes down one folder level atm
    if ProcessOps.NO_POSTPROCESSING not in options:
        total_files = sum(len(os.listdir(path)) for path in folder_paths)
        typer.secho(
            f"Applying processing options: {', '.join(options)} to {total_files} images"
        )

        # TODO: move async/multiprocessing into iohandler or processing
        # if processing probably rename iohandler to downloader
        with typer.progressbar(
            mandown.process_progress(folder_paths, options, maxthreads),
            length=total_files,
            label="Processing",
        ) as progress:
            for _ in progress:
                pass


@app.command()
def process(
    options: list[ProcessOps],
    folder_path: Path = typer.Argument(Path(os.getcwd())),
    maxthreads: int = typer.Option(
        4,
        "--threads",
        "-t",
        help="The maximum number of images to process in parallel",
    ),
) -> None:
    """
    Process a folder of images recursively in-place.
    """
    image_paths = list(map(Path, filter(os.path.isdir, folder_path.iterdir())))
    cli_process(image_paths, options, maxthreads)


@app.command()
def convert(
    convert_to: ConvertFormats,
    folder_path: Path,
    metadata_source: Optional[str] = typer.Option(
        None, "--metadata-from", "-m", help="The source to embed metadata from"
    ),
    dest: Path = typer.Option(
        os.getcwd(), "--dest", "-d", help="The folder to save the converted file to."
    ),
    maxthreads: int = typer.Option(
        4,
        "--threads",
        "-t",
        help="The maximum number of images to process in parallel",
    ),
) -> None:
    """
    Convert a folder of images into a comic a la KCC. Optionally
    embed metadata from an online source.
    """
    metadata = cli_query(metadata_source).metadata if metadata_source else None
    cli_convert(folder_path, convert_to, dest, metadata)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        is_eager=True,
        help="Display the current version of mandown",
    ),
    supported_sites: Optional[bool] = typer.Option(
        None,
        "--supported-sites",
        is_eager=True,
        help="Output a list of domains supported by mandown",
    ),
) -> None:
    if version:
        typer.echo(f"mandown {importlib.metadata.version('mandown')}")
        raise typer.Exit()

    if supported_sites:
        for source in mandown.sources.get_all_classes():
            typer.echo(f"{source.name}: {', '.join(source.domains)}")
        raise typer.Exit()


# pylint: disable=unused-argument
@app.command()
def download(
    url: str,
    dest: str = typer.Argument(
        os.getcwd(), help="The destination folder to download to."
    ),
    convert_to: ConvertFormats = typer.Option(
        "folder", "--convert", "-c", help="The format to download the comic as"
    ),
    start: Optional[int] = typer.Option(
        None,
        "--start",
        "-s",
        help="The first chapter to download [default: first found]",
    ),
    end: Optional[int] = typer.Option(
        None, "--end", "-e", help="The last chapter to download [default: last found]"
    ),
    maxthreads: int = typer.Option(
        4,
        "--threads",
        "-t",
        help="The maximum number of images to download in parallel",
    ),
    processing_options: Optional[List[ProcessOps]] = typer.Option(
        [],
        "--processing-options",
        "-p",
        help="Image processing options (in-place)",
        case_sensitive=True,
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if not os.path.isdir(dest):
        raise ValueError(f"{dest} is not a valid folder path.")

    # get metadata
    source = cli_query(url)

    # starting to think that immutability is much better than whatever
    # the heck is going on here
    target_path = os.path.join(dest, source.metadata.title)
    if not os.path.isdir(target_path):
        os.mkdir(target_path)

    # get processing range
    start_chapter = start or 1
    end_chapter = end or len(source.chapters)

    # zero-index
    start_chapter -= 1

    # download
    chapter_range: list[Chapter] = []
    # yikes these should be split into their own functions sometime
    # get cover art
    with open(Path(target_path) / "cover.jpg", "w+b") as file:
        file.write(requests.get(source.metadata.cover_art).content)

    chapter_range = source.chapters[start_chapter:end_chapter]
    typer.echo("Downloading...")
    for i, chapter in enumerate(chapter_range):
        with typer.progressbar(
            mandown.download_chapter_progress(chapter, target_path, maxthreads),
            length=len(chapter.images),
            label=f"{chapter.title} ({i+1}/{len(chapter_range)})",
        ) as progress:
            for _ in progress:
                pass
    typer.secho(
        f"Successfully downloaded {len(chapter_range)} chapters.",
        fg=typer.colors.GREEN,
    )

    # process
    if processing_options:
        image_paths = list(map(Path, filter(os.path.isdir, os.listdir(target_path))))
        cli_process(image_paths, processing_options)

    # convert
    if convert_to != ConvertFormats.FOLDER:
        cli_convert(
            target_path,
            convert_to,
            dest,
            source.metadata,
            [(c.title, c.title_sanitised) for c in chapter_range],
        )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
