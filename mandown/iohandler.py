"""
Handles downloading files
"""
import multiprocessing as mp
import os
from typing import Iterable

import requests


def async_download(data: tuple[str, str, dict[str, str]]) -> None:
    url, dest_folder, headers = data
    name = url.split("/")[-1]
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

    map_pool = list(map(lambda url: (url, dest_folder, headers), urls))

    with mp.Pool(maxthreads) as pool:
        for i in pool.imap_unordered(async_download, map_pool):
            yield i
