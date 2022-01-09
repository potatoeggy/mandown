#!/usr/bin/env python3

import os
from typing import Optional

import typer

from mandown import mandown as md
from mandown.sources.base_source import BaseSource

app = typer.Typer()


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
        1, help="The maximum number of images to download in parallel."
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if not os.path.isdir(dest):
        raise ValueError(f"{dest} is not a valid folder path.")

    source: BaseSource = md.query(url)

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

    for i, chapter in enumerate(source.chapters[start_chapter:end_chapter]):
        print(f"Downloading {chapter.title} ({i+1}/{len(source.chapters)})...")
        md.download_chapter(chapter, target_path, maxthreads)
    print("Done.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
