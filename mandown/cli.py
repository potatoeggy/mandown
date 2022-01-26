#!/usr/bin/env python3

import importlib.metadata
import os
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Optional

import requests
import typer

import mandown.sources
from mandown import mandown
from mandown.converter import Converter
from mandown.sources.base_source import BaseSource

app = typer.Typer()


class ConvertFormats(str, Enum):
    CBZ = "cbz"
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"
    FOLDER = "folder"


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mandown {importlib.metadata.version('mandown')}")
        raise typer.Exit()


def supported_sites_callback(value: bool) -> None:
    if value:
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
    convert: ConvertFormats = typer.Option(
        "folder", "--convert", "-c", help="The format to download the comic as"
    ),
    from_folder: Path = typer.Option(
        None,
        "--from",
        help="The folder to assume the comic exists in to convert without downloading",
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
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Display the current version of mandown",
    ),
    supported_sites: Optional[bool] = typer.Option(
        None,
        "--supported-sites",
        callback=supported_sites_callback,
        is_eager=True,
        help="Output a list of domains supported by mandown",
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if not os.path.isdir(dest):
        raise ValueError(f"{dest} is not a valid folder path.")

    typer.echo(f"Searching sources for {url}")
    try:
        source: BaseSource = mandown.query(url, populate=True)
        typer.secho(f'Found item from source "{source.name}"', fg=typer.colors.GREEN)
        typer.secho(source)
    except ValueError as err:
        typer.secho("Could not match URL with available sources.", fg=typer.colors.RED)
        raise typer.Exit(1) from err

    # starting to think that immutability is much better than whatever
    # the heck is going on here
    target_path = os.path.join(dest, source.metadata.title)
    if not os.path.isdir(target_path):
        os.mkdir(target_path)

    # if they are undefined
    start_chapter = start or 1
    end_chapter = end or len(source.chapters)

    # zero-index
    start_chapter -= 1

    chapter_range = []
    if (
        from_folder is None
    ):  # yikes these should be split into their own functions sometime
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
    else:
        if convert.value == ConvertFormats.FOLDER:
            typer.secho(
                "A convert format was not specified but is required for conversion.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        if start or end:
            typer.secho(
                "WARNING: --start and --end have no effect when --from is used",
                fg=typer.colors.BRIGHT_RED,
            )
        target_path = str(from_folder)

    if convert.value != ConvertFormats.FOLDER:
        typer.echo(f"Converting to {convert.value}...")

        formatted_chapters = [(c.title, c.title_sanitised) for c in chapter_range]
        converter = Converter(
            target_path,
            source.metadata,
            chapter_list=None if from_folder else formatted_chapters,
        )

        convert_func: Callable[[str], Iterable] = lambda i: None
        match convert.value:
            case ConvertFormats.EPUB:
                convert_func = converter.to_epub_progress
            case ConvertFormats.CBZ:
                convert_func = converter.to_cbz_progress
            case ConvertFormats.MOBI:
                raise ValueError("MOBI conversion is not yet supported.")
            case ConvertFormats.PDF:
                raise ValueError("PDF conversion is not yet supported.")

        with typer.progressbar(
            length=converter.max_operations[convert.value], label="Converting"
        ) as progress:
            for i in convert_func(dest):
                progress.update(1, i)

        dest_file = dest / Path(source.metadata.title).with_suffix(f".{convert.value}")
        typer.secho(f"Successfully converted to {dest_file}", fg=typer.colors.GREEN)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
