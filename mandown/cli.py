#!/usr/bin/env python3

from pathlib import Path
from typing import cast

import comicon
import typer

from . import (
    MD_METADATA_FILE,
    BaseChapter,
    BaseComic,
    BaseMetadata,
    ConvertFormats,
    ProcessConfig,
    ProcessOps,
    ProcessOptionMismatchError,
    SupportedProfiles,
    __version_str__,
    all_profiles,
    api,
    sources,
)
from .errors import ImageDownloadError

app = typer.Typer()


def cli_init_metadata_interactive() -> None:
    path: Path = typer.prompt("Folder path", default=Path.cwd(), type=Path).expanduser().resolve()

    try:
        comic = api.load(path)
    except FileNotFoundError:
        # expected if no metadata exists
        ...
    except IOError as err:
        typer.secho(f"{path} could not be found. Does it exist?", fg=typer.colors.RED)
        raise typer.Exit(1) from err
    else:
        typer.secho(
            f"There is already a comic at {path}. Remove md-metadata.json"
            "if you're sure you want to restart!",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    no_url_sentinel = "None"
    source_url: str = typer.prompt(
        "Automatically populate with the following source URL", default=no_url_sentinel
    )

    metadata = BaseMetadata("", [], "", [], "", "")
    chapters: list[BaseChapter] = []

    if source_url != no_url_sentinel:
        comic = cli_query(source_url)
        typer.echo(f"Found {comic.metadata.title} with {len(comic.chapters)} chapters")
        metadata = comic.metadata
        chapters = comic.chapters

    metadata.title = typer.prompt("Title", default=metadata.title or None).strip()
    metadata.__post_init__()  # regenerate slug

    metadata.authors = [
        s.strip()
        for s in typer.prompt(
            "Author(s) (comma-separated)",
            default=", ".join(metadata.authors) or None,
        ).split(",")
    ]
    metadata.genres = [
        s.strip()
        for s in typer.prompt(
            "Genre(s) (comma-separated)",
            default=", ".join(metadata.genres) or None,
        ).split(",")
    ]
    metadata.cover_art = typer.prompt(
        "Cover art URL (enter 'EXISTS' if cover.png/jpg already exists)",
        default=metadata.cover_art or None,
    ).strip()
    metadata.description = typer.prompt("Description", default=metadata.description or None).strip()
    metadata.url = metadata.url

    typer.secho("Metadata collected, now adding chapters...", fg=typer.colors.GREEN)

    folders_in_cd = sorted(f for f in path.iterdir() if f.is_dir())
    delta = len(folders_in_cd)  # #folders - #chapters
    if chapters:
        # try to match up chapters with existing files
        for folder, chapter in zip(folders_in_cd, chapters, strict=False):
            chapter.slug = folder.stem

        # print out the matches
        typer.secho("Matches found:", fg=typer.colors.GREEN)
        for folder, chapter in zip(folders_in_cd, chapters, strict=False):
            typer.echo(f"  {folder.stem} -> {chapter.title}")

        delta = len(folders_in_cd) - len(chapters)

    if delta > 0:
        res = typer.prompt(
            f"Matching stalled with {delta} extra local chapters. Attempt to resolve? [Y/n]",
            default=True,
            show_choices=True,
            show_default=False,
        )
        if res:
            # if there are more folders than chapters, add them as new chapters
            for folder in folders_in_cd[len(chapters) :]:
                chapters.append(BaseChapter(folder.stem, "", folder.stem))

            # print out new matches
            typer.secho("New chapters:", fg=typer.colors.GREEN)
            for folder, _ in zip(folders_in_cd, chapters, strict=False):
                typer.echo(f"  NEW: {folder.stem}")

    res = typer.prompt(
        "Matching completed. Finish and save? [Y/n]",
        default=True,
        show_choices=True,
        show_default=False,
    )

    if not res:
        raise typer.Abort()

    typer.secho(
        f"All done! Saving metadata to {path / MD_METADATA_FILE}...",
        fg=typer.colors.GREEN,
    )
    api.init_parse_comic(path, BaseComic(metadata, chapters), metadata.cover_art != "EXISTS")


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
    split_by_chapters: bool = False,
) -> None:
    comic = api.load(comic_path)
    iterator = api.convert_progress(
        comic_path, target_format, dest_folder, remove_after, split_by_chapters
    )

    is_single_conversion = comic_path.is_dir()

    try:
        len_first_conv = cast(int, next(iterator))
    except comicon.errors.BadImageError as err:
        typer.secho(str(err), fg=typer.colors.RED)
        if "webp" in str(err):
            typer.secho(
                "WebP images cannot be converted. Consider"
                " first applying the processing option `webp_to_png`.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(2) from None
    except RuntimeError as err:
        # handle kindlegen errors
        typer.secho(str(err), fg=typer.colors.RED)
        raise typer.Abort() from None

    len_second_conv = -1

    first_convert_message = (
        f"Packing {target_format.value}(s)" if is_single_conversion else "Pre-converting comic"
    )

    try:
        with typer.progressbar(
            iterator,
            length=len_first_conv,
            label=first_convert_message,
        ) as progress:
            for res in progress:
                if isinstance(res, int):
                    len_second_conv = res
                    break
                if split_by_chapters:
                    progress.label = res
    except RuntimeError as err:
        # handle kindlegen errors
        typer.secho(str(err), fg=typer.colors.RED)
        raise typer.Abort() from None

    if not is_single_conversion:
        # it *should* be guaranteed len_second_conv exists
        try:
            with typer.progressbar(
                iterator,
                length=len_second_conv,
                label=f"Packing {target_format.value}",
            ) as progress:
                for _ in progress:
                    ...
        except RuntimeError as err:
            # handle kindlegen errors
            typer.secho(str(err), fg=typer.colors.RED)
            raise typer.Abort() from None

    if not split_by_chapters:
        dest_file = dest_folder / f"{comic.metadata.title_slug}.{target_format.value}"
        typer.secho(f"Successfully converted to {dest_file}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Successfully converted to {dest_folder}", fg=typer.colors.GREEN)


def cli_process(comic_path: Path, options: list[ProcessOps], config: ProcessConfig) -> None:
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

    typer.secho(f"Applying processing options: {', '.join(options)}", fg=typer.colors.GREEN)
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


@app.command(no_args_is_help=True)
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
    split_by_chapters: bool = typer.Option(
        False,
        "--split-by-chapters",
        "-b",
        help="Instead of returning one large comic file, create one comic"
        "file for each chapter (applies only to Mandown-created comic folders)",
    ),
) -> None:
    """
    Convert a comic OR comic folder into CBZ/EPUB/PDF.

    eg. To convert to CBZ:
    mandown convert cbz /path/to/comic/folder

    eg. To convert an existing PDF comic to EPUB:
    mandown convert epub /path/to/comic.pdf
    """
    typer.echo(f"Converting to {convert_to}...")
    cli_convert(folder_path, convert_to, dest, remove_after, split_by_chapters)


@app.command(no_args_is_help=True)
def process(
    options: list[ProcessOps],
    folder_path: Path = typer.Argument(Path.cwd()),
    target_size: tuple[int, int] | None = typer.Option(
        (0, 0),
        "--target-size",
        "-z",
        min=0,
        show_default=False,
        help="RESIZE ONLY: The target size (width, height) (cannot be used with `profile`)",
    ),
    size_profile: str | None = typer.Option(
        None,
        "--profile",
        "-o",
        help="RESIZE ONLY: The device profile to use (cannot be used with `target-size`)",
    ),
) -> None:
    """
    Process a comic folder in-place.

    eg. To trim borders and resize to 800x1200:
    mandown process trim_borders resize -z 800 1200

    eg. To split double pages and resize to a Kindle Paperwhite 2 profile:
    mandown process split_double_pages resize -o paper

    All profiles can be listed with "mandown --list-profiles".
    """
    # work around typer bug (see mandown get)
    if target_size == (0, 0):
        target_size = None

    size_profile = cast(SupportedProfiles | None, size_profile)

    try:
        config = ProcessConfig(
            target_size=target_size,
            output_profile=size_profile,
        )
    except Exception as err:
        typer.secho(f"Could not apply processing options: {err}", fg=typer.colors.RED)
        raise typer.Exit(1) from err
    cli_process(folder_path, options, config)


@app.command(no_args_is_help=True)
def get(
    url: str,
    dest: Path = typer.Argument(Path.cwd(), help="The destination folder to download to."),
    convert_to: ConvertFormats = typer.Option(
        "none", "--convert", "-c", help="The format to download the comic as"
    ),
    start: int | None = typer.Option(
        None,
        "--start",
        "-s",
        help="The first chapter to download [default: first found]",
    ),
    end: int | None = typer.Option(
        None, "--end", "-e", help="The last chapter to download [default: last found]"
    ),
    maxthreads: int = typer.Option(
        4,
        "--threads",
        "-t",
        help="The maximum number of images to download in parallel",
    ),
    processing_options: list[ProcessOps] | None = typer.Option(
        [],
        "--process",
        "-p",
        help="Image processing options (in-place)",
        case_sensitive=True,
    ),
    target_size: tuple[int, int] | None = typer.Option(
        (0, 0),
        "--target-size",
        "-z",
        show_default=False,
        min=0,
        help="IF PROCESSING AND RESIZING: The target size (width, height)",
    ),
    size_profile: str | None = typer.Option(
        None,
        "--profile",
        "-o",
        help="IF PROCESSING AND RESIZING: The device profile to use",
    ),
    remove_after: bool = typer.Option(
        False,
        "--remove-after",
        "-r",
        help="IF CONVERTING: Remove the downloaded folder after converting",
    ),
    split_by_chapters: bool = typer.Option(
        False,
        "--split-by-chapters",
        "-b",
        help="IF CONVERTING: Instead of returning one large comic file, create one comic"
        "file for each chapter (applies only to Mandown-created comic folders)",
    ),
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.

    eg. To download all chapters of a comic to the current directory:
    mandown get https://website.com/comic/1234

    eg. To download chapters 1-10 of a comic to the current directory:
    mandown get https://website.com/comic/1234 -s 1 -e 10

    eg. To convert all chapters of a comic to EPUB:
    mandown get https://website.com/comic/1234 -c epub

    eg. To convert all chapters of a comic to CBZ after trimming borders:
    mandown get https://website.com/comic/1234 -c cbz -p trim_borders
    """
    # work around typer bug (optional of tuples is not parsed correctly)
    if target_size == (0, 0):
        target_size = None

    if not dest.is_dir():
        raise ValueError(f"{dest} is not a valid folder path.")

    size_profile = cast(SupportedProfiles | None, size_profile)

    # get and save metadata
    comic = cli_query(url)

    typer.echo(
        f'Found comic "{comic.metadata.title}" from source {sources.get_class_for(url).name}',
    )

    # get processing range
    start_chapter = start or 1
    end_chapter = end or len(comic.chapters)

    # zero-index
    start_chapter -= 1

    comic.set_chapter_range(start=start_chapter, end=end_chapter)

    # download
    typer.echo(f"Downloading {end_chapter - start_chapter} chapter(s)...")
    try:
        with typer.progressbar(
            api.download_progress(comic, dest, threads=maxthreads),
            length=len(comic.chapters),
        ) as progress:
            for title in progress:
                progress.label = title
    except ImageDownloadError as err:
        typer.secho(
            "Some image links on the host site were broken, exiting...",
            fg=typer.colors.BRIGHT_YELLOW,
        )
        typer.secho(f"Error: {err}", fg=typer.colors.RED)
        raise typer.Abort(3) from err

    full_dest_folder = dest.absolute() / comic.metadata.title_slug
    typer.secho(
        f"Successfully downloaded {end_chapter - start_chapter} chapter(s) to {full_dest_folder}.",
        fg=typer.colors.GREEN,
    )

    # process
    if processing_options:
        try:
            config = ProcessConfig(
                target_size=target_size,
                output_profile=size_profile,
            )
        except Exception as err:
            typer.secho(f"Could not apply processing options: {err}", fg=typer.colors.RED)
            raise typer.Exit(1) from err

        cli_process(dest / comic.metadata.title_slug, processing_options, config)

    # convert
    if convert_to != ConvertFormats.NONE:
        cli_convert(
            dest / comic.metadata.title_slug,
            convert_to,
            dest,
            remove_after,
            split_by_chapters,
        )


@app.command(name="init-metadata")
def init_metadata(
    path: Path | None = typer.Argument(None, help="The folder to initialise"),
    source_url: str | None = typer.Argument(None, help="The url to get metadata from"),
    download_cover: bool = typer.Option(
        False,
        "--download-cover",
        "-d",
        help="If --source-url is passed: Download the cover image from the source.",
    ),
) -> None:
    """
    Initialise a folder with metadata to be converted with Mandown, optionally
    fetching metadata from an internet source. Pass with no arguments to
    start an interactive session.

    eg. mandown init-metadata /path/to/folder https://website.com/comic/1234 --download-cover
    """

    if path is None:
        # interactive session
        return cli_init_metadata_interactive()

    if (path / MD_METADATA_FILE).is_file():
        return typer.echo("Metadata already found. Please remove it to create new metadata.")

    try:
        if source_url is not None:
            donor = api.query(source_url)
            comic = api.init_parse_comic(path, donor, download_cover)
        else:
            comic = api.init_parse_comic(path)
    except AttributeError as err:
        typer.secho("--download-cover must be used with --source-url.")
        raise typer.Exit(1) from err
    except ValueError as err:
        typer.secho("Source not found.")
        raise typer.Exit(1) from err

    typer.secho(f"Found {comic.metadata.title}:", fg=typer.colors.BRIGHT_GREEN)
    typer.echo(comic)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def callback(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        is_eager=True,
        help="Display the current version of mandown",
    ),
    supported_sites: bool | None = typer.Option(
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
            "\n".join(f" - {profile.name}: {profile.id!r}" for profile in all_profiles.values())
        )
        raise typer.Exit()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
