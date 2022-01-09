"""
Handles downloading files
"""
import multiprocessing as mp
import os

import requests


def async_download(url: str, dest_folder: str) -> None:
    name = url.split("/")[-1]
    dest_file = os.path.join(dest_folder, name)

    response = requests.get(url)
    response.raise_for_status()
    with open(dest_file, "wb") as file:
        file.write(response.content)


def download(urls: list[str] | str, dest_folder: str, maxthreads: int = 1) -> None:
    """
    Download one or multiple URLs to a destination folder.
    Raises ValueError if the folder does not exist.
    """
    if isinstance(urls, str):
        urls = [urls]

    if not os.path.isdir(dest_folder):
        raise ValueError(f"Folder path {dest_folder} does not exist")

    print(f"{len(urls)} links found.")
    map_pool = list(map(lambda url: (url, dest_folder), urls))

    with mp.Pool(maxthreads) as pool:
        pool.starmap(async_download, map_pool)
