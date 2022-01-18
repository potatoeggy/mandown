"""
Handles downloading files
"""
# pylint: disable=invalid-name
import multiprocessing as mp
import os
import urllib.parse
from typing import Iterable, Optional

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


def download(
    urls: list[str] | str,
    dest_folder: str,
    headers: dict[str, str] = None,
    maxthreads: int = 1,
) -> Iterable[None]:
    """
    Download one or multiple URLs to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    if isinstance(urls, str):
        urls = [urls]

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    map_pool: list[tuple[str, str, str, Optional[dict[str, str]]]] = []
    for i, u in enumerate(urls):
        _, ext = os.path.splitext(urllib.parse.urlparse(u).path)
        map_pool.append((u, dest_folder, f"{str(i + 1)}{ext}", headers))

    with mp.Pool(maxthreads) as pool:
        for c in pool.imap_unordered(async_download, map_pool):
            yield c
