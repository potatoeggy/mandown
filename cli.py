#!/usr/bin/env python3

import typer
from mangadownloader import mangadownloader as md

app = typer.Typer()


@app.command()
def download(
    url: str,
    dest_folder: str,
    start_chapter: int | None = None,
    end_chapter: int | None = None,
) -> None:
    md.download(url, dest_folder, start_chapter, end_chapter)


if __name__ == "__main__":
    app()
