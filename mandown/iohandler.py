"""
Handles downloading files
"""
# pylint: disable=invalid-name
import imghdr
import multiprocessing as mp
import os
from pathlib import Path
import urllib.parse
from typing import Iterable, Optional, Sequence

import requests


def async_download(
    data: tuple[str, str, Optional[str], Optional[dict[str, str]]]
) -> None:
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

    map_pool: list[tuple[str, str, str, Optional[dict[str, str]]]] = []
    padding = f"0{len(str(len(urls)))}"
    if filestems is None:
        filestems = [f"{i+1:{padding}}" for i in range(len(urls))]

    for u, stem in zip(urls, filestems, strict=True):
        _, ext = os.path.splitext(urllib.parse.urlparse(u).path)

        map_pool.append((u, dest_folder, f"{stem}{ext}", headers))

    with mp.Pool(maxthreads) as pool:
        yield from pool.imap_unordered(async_download, map_pool)
