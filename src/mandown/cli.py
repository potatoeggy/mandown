#!/usr/bin/env python3

import typer
from mandown import mandown as md

app = typer.Typer()


@app.command()
def download(
    url: str,
    dest_folder: str,
    start: int | None = None,
    end: int | None = None,
    maxthreads: int = 1,
) -> None:
    md.download(url, dest_folder, start, end, maxthreads)


if __name__ == "__main__":
    app()
