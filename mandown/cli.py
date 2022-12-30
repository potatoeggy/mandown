#!/usr/bin/env python3

from pathlib import Path
from typing import List, Optional

import typer

from . import (
    MD_METADATA_FILE,
    BaseComic,
    ConvertFormats,
    ProcessConfig,
    ProcessOps,
    ProcessOptionMismatchError,
    __version_str__,
    all_profiles,
    api,
    sources,
)

app = typer.Typer()


def cli_query(url: str) -> BaseComic:
    typer.echo(f"Searching sources for {url}")

    try:
        comic = api.query(url)
    except ValueError as err:
        typer.secho("Could not match URL with available sources.", fg=typer.colors.RED)
        raise typer.Exit(1) from err
    return comic


def cli_convert(
    comic_path: Path,
    target_format: ConvertFormats,
    dest_folder: Path = Path.cwd(),
    remove_after: bool = False,
) -> None:
    try:
        comic = api.load(comic_path)
    except FileNotFoundError as err:
        typer.secho(
            f"Comic not found at {comic_path}, is md-metadata.json missing?",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from err

    with typer.progressbar(
        api.convert_progress(
            comic, comic_path, target_format, dest_folder, remove_after
        ),
        length=len(comic.chapters),
        label="Converting",
    ) as progress:
        for _ in progress:
            pass
    dest_file = dest_folder / f"{comic.metadata.title}.{target_format.value}"
    typer.secho(f"Successfully converted to {dest_file}", fg=typer.colors.GREEN)


def cli_process(
    comic_path: Path, options: list[ProcessOps], config: ProcessConfig
) -> None:
    if ProcessOps.NO_POSTPROCESSING in options:
        return

    try:
        comic = api.load(comic_path)
    except FileNotFoundError as err:
        typer.secho(
            f"Comic not found at {comic_path}, is md-metadata.json missing?",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from err

    typer.secho(
        f"Applying processing options: {', '.join(options)}", fg=typer.colors.GREEN
    )
    try:
        with typer.progressbar(
            api.process_progress(comic_path, options, config),
            length=len(comic.chapters),
            label="Processing",
        ) as progress:
            for _ in progress:
                pass
    except ProcessOptionMismatchError as err:
        typer.secho(f"Could not apply processing options: {err}", fg=typer.colors.RED)
        raise typer.Exit(1) from err


@app.command()
def convert(
    convert_to: ConvertFormats,
    folder_path: Path,
    dest: Path = typer.Option(
        Path.cwd(),
        "--dest",
        "-d",
        help="The folder to save the converted file to.",
    ),
    remove_after: bool = typer.Option(
        False,
        "--remove-after",
        "-r",
        help="Remove the the original folder after conversion",
    ),
) -> None:
    """
    Convert a comic folder into CBZ/EPUB/PDF.
    """
    try:
        comic = api.load(folder_path)
    except FileNotFoundError as err:
        typer.secho(
            f"Comic not found at {folder_path}, is md-metadata.json missing?",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from err

    typer.echo(
        f"Found {comic.metadata.title} with {len(comic.chapters)} chapters, "
        f"converting to {convert_to}..."
    )
    cli_convert(folder_path, convert_to, dest, remove_after)


@app.command()
def process(
    options: list[ProcessOps],
    folder_path: Path = typer.Argument(Path.cwd()),
    target_size: Optional[tuple[int, int]] = typer.Option(
        None,
        "--target-size",
        "-z",
        help="RESIZE ONLY: The target size (width, height) (cannot be used with `profile`)",
    ),
    size_profile: Optional[SupportedProfilesEnum] = typer.Option(
        None,
        "--profile",
        "-p",
        help="RESIZE ONLY: The device profile to use (cannot be used with `target-size`)",
    ),
) -> None:
    """
    Process a comic folder in-place.
    """

    config = ProcessConfig(
        target_size=target_size,
        output_profile=size_profile.value if size_profile else None,
    )
    cli_process(folder_path, options, config)


@app.command()
def get(
    url: str,
    dest: Path = typer.Argument(
        Path.cwd(), help="The destination folder to download to."
    ),
    convert_to: ConvertFormats = typer.Option(
        "none", "--convert", "-c", help="The format to download the comic as"
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
    target_size: Optional[tuple[int, int]] = typer.Option(
        None,
        "--target-size",
        "-z",
        help="IF PROCESSING AND RESIZING: The target size (width, height)",
    ),
    size_profile: Optional[SupportedProfilesEnum] = typer.Option(
        None,
        "--profile",
        "-p",
        help="IF PROCESSING AND RESIZING: The device profile to use",
    ),
    remove_after: bool = typer.Option(
        False,
        "--remove-after",
        "-r",
        help="IF CONVERTING: Remove the downloaded folder after converting",
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if not dest.is_dir():
        raise ValueError(f"{dest} is not a valid folder path.")

    # get and save metadata
    comic = cli_query(url)

    typer.echo(
        f"Found item from source {sources.get_class_for(url).name}",
    )

    # get processing range
    start_chapter = start or 1
    end_chapter = end or len(comic.chapters)

    # zero-index
    start_chapter -= 1

    comic.set_chapter_range(start=start_chapter, end=end_chapter)

    # download
    typer.echo("Downloading...")
    with typer.progressbar(
        api.download_progress(comic, dest, threads=maxthreads),
        length=len(comic.chapters),
    ) as progress:
        for title in progress:
            progress.label = title
    typer.secho(
        f"Successfully downloaded {end_chapter - start_chapter} chapters.",
        fg=typer.colors.GREEN,
    )

    # process
    if processing_options:
        config = ProcessConfig(
            target_size=target_size,
            output_profile=size_profile.value if size_profile else None,
        )
        cli_process(dest / comic.metadata.title, processing_options, config)

    # convert
    if convert_to != ConvertFormats.NONE:
        cli_convert(dest / comic.metadata.title, convert_to, dest, remove_after)


@app.command(name="init-metadata")
def init_metadata(
    path: Path,
    source_url: Optional[str] = typer.Argument(
        None, help="The url to get metadata from"
    ),
) -> None:
    """
    Initialise a folder with metadata to be converted with Mandown, optionally
    fetching metadata from an internet source.
    """
    if (path / MD_METADATA_FILE).is_file():
        return typer.echo(
            "Metadata already found. Please remove it to create new metadata."
        )
    comic = api.init_parse_comic(path, source_url)
    typer.secho(f"Found {comic.metadata.title}:", fg=typer.colors.BRIGHT_GREEN)
    typer.echo(comic)


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
    list_profiles: bool = typer.Option(
        False,
        "--list-profiles",
        "-l",
        help="List available device profiles and details",
        is_eager=True,
    ),
) -> None:
    if version:
        typer.echo(f"mandown {__version_str__}")
        raise typer.Exit()

    if supported_sites:
        for source in sources.get_all_classes():
            typer.echo(f"{source.name}: {', '.join(source.domains)}")
        raise typer.Exit()

    if list_profiles:
        typer.echo("Available profiles:")
        typer.echo(
            "\n".join(
                f' - {profile.name}: "{profile.id}"'
                for profile in all_profiles.values()
            )
        )
        raise typer.Exit()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
