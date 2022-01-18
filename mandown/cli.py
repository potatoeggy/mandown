#!/usr/bin/env python3

import importlib.metadata
import os
from typing import Optional

import typer

from mandown import mandown as md
from mandown.sources.base_source import BaseSource

app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mandown {importlib.metadata.version('mandown')}")
        raise typer.Exit()


@app.command()
def download(
    url: str,
    dest: str = typer.Option(
        os.getcwd(), help="The destination folder to download to."
    ),
    start: Optional[int] = typer.Option(
        None, help="The first chapter to download [default: first found]"
    ),
    end: Optional[int] = typer.Option(
        None, help="The last chapter to download [default: last found]"
    ),
    maxthreads: int = typer.Option(
        4, help="The maximum number of images to download in parallel."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Display the current version of mandown",
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if version:
        return

    if not os.path.isdir(dest):
        raise ValueError(f"{dest} is not a valid folder path.")

    typer.echo(f"Searching sources for {url}")
    try:
        source: BaseSource = md.query(url, populate=True)
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

    chapter_range = source.chapters[start_chapter:end_chapter]
    for i, chapter in enumerate(chapter_range):
        with typer.progressbar(
            md.download_chapter(chapter, target_path, maxthreads),
            length=len(chapter.images),
            label=f"{chapter.title} ({i+1}/{len(chapter_range)})",
        ) as progress:
            for _ in progress:
                pass
    typer.secho(
        f"Successfully downloaded {len(chapter_range)} chapters.", fg=typer.colors.GREEN
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
