"""
Handles downloading files
"""
# pylint: disable=invalid-name
import dataclasses
import imghdr
import json
import multiprocessing as mp
import os
import urllib.parse
from pathlib import Path
from typing import Iterable, Sequence

import requests
from pydantic import BaseModel

from mandown.sources.base_source import Chapter, MangaMetadata

METADATA_PATH_NAME = "md-metadata.json"


def async_download(data: tuple[str, str, str | None, dict[str, str] | None]) -> None:
    url, dest_folder, filename, headers = data
    name = filename or url.split("/")[-1]
    dest_file = os.path.join(dest_folder, name)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(dest_file, "wb") as file:
        file.write(response.content)

    # if the file extension is lying
    # rename it so epubcheck doesn't yell at us
    ext = imghdr.what(dest_file)
    if ext is not None:
        os.rename(dest_file, Path(dest_file).with_suffix(f".{ext}"))


def download(
    urls: Sequence[str] | str,
    dest_folder: str,
    headers: dict[str, str] = None,
    maxthreads: int = 1,
    filestems: Sequence[str] | str | None = None,
) -> Iterable[None]:
    """
    Download one or multiple URLs to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    if isinstance(urls, str):
        urls = [urls]

    if isinstance(filestems, str):
        filestems = [filestems]

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    map_pool: list[tuple[str, str, str, dict[str, str] | None]] = []
    padding = f"0{len(str(len(urls)))}"
    if filestems is None:
        filestems = [f"{i+1:{padding}}" for i in range(len(urls))]

    for u, stem in zip(urls, filestems, strict=True):
        _, ext = os.path.splitext(urllib.parse.urlparse(u).path)

        map_pool.append((u, dest_folder, f"{stem}{ext}", headers))

    with mp.Pool(maxthreads) as pool:
        yield from pool.imap_unordered(async_download, map_pool)


class FileSystemChapterValidator(BaseModel):
    title: str
    rel_path: str

    def to_discrete(self) -> Chapter:
        pass  # this doesn't work unless we refactor that too


class FileSystemMetadataValidator(BaseModel):
    title: str
    authors: list[str]
    url: str
    genres: list[str]
    description: str
    cover_art_url: str
    chapters: list[FileSystemChapterValidator]

    def to_discrete(self) -> MangaMetadata:
        # TODO: merge MangaMetadata and the FileSystemValidators
        return MangaMetadata(
            self.title,
            self.authors,
            self.url,
            self.genres,
            self.description,
            self.cover_art_url,
        )


class FileSystemComic:
    def __init__(
        self,
        path: Path | str,
        *,
        metadata: MangaMetadata | None = None,
        chapters: list[Chapter] | None = None,
    ):
        """
        Attempt to open a new comic ready for writing.

        @param `path`: File path to open
        @param `create`: Create the file path if it does not exist
        @param `metadata`: Use existing metadata if available
        @param `chapters`: Use existing chapter data if available
        """
        path = Path(path)
        self.path = path

        # create the folder, failing gracefully
        # if the folder already exists
        path.mkdir(exist_ok=True)

        try:
            self._populate_from_path(path)
        except IOError:
            pass  # expected if doesn't exist

        if metadata is not None:
            self.metadata = metadata

        if chapters is not None:
            self.chapters = chapters

    def _populate_from_path(self, path: Path) -> None:
        with open(path / METADATA_PATH_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        validated_data = FileSystemMetadataValidator(**data)
        self.metadata = validated_data.to_discrete()
        self.chapters = [c.to_discrete() for c in validated_data.chapters]

    def save(self) -> None:
        data = dataclasses.asdict(self.metadata)
        data["chapters"] = [dataclasses.asdict(c) for c in self.chapters]

        with open(self.path / METADATA_PATH_NAME, "w", encoding="utf-8") as file:
            json.dump(data, file)
