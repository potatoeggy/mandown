# pylint: disable=invalid-name
import sys
import types

from .base_source import BaseSource

from . import (  # isort: skip
    source_mangadex,
    source_mangakakalot,
    source_manganato,
    source_mangasee,
    source_readcomiconline,
    source_webtoons,
)

__class_list: list[type[BaseSource]] = []


def _get_all_source_modules() -> list[str]:
    out = []
    for _, val in globals().items():
        if isinstance(val, types.ModuleType) and val.__name__.startswith(
            "mandown.sources.source_"
        ):
            out.append(val.__name__)
    return out


for i in _get_all_source_modules():
    __class_list.append(sys.modules[i].get_class())


def get_class_for(url: str) -> type[BaseSource]:
    """
    Return a source that matches the URL.
    """
    for c in __class_list:
        if c.check_url(url):
            return c
    raise ValueError("No sources found matched the URL query.")


def get_all_classes() -> list[type[BaseSource]]:
    """
    Return all imported source module classes. Best used for manual poking.
    """
    return __class_list
