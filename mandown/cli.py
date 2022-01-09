#!/usr/bin/env python3

import os

import typer

from mandown import mandown as md

app = typer.Typer()


@app.command()
def download(
    url: str,
    dest: str = typer.Option(
        os.getcwd(), help="The destination folder to download to."
    ),
    start: int | None = None,
    end: int | None = None,
    maxthreads: int = 1,
) -> None:
    md.download(url, dest, start, end, maxthreads)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
