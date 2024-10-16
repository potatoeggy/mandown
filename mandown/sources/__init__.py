# pylint: disable=invalid-name

"""
This module contains all the source modules.

The source modules are dynamically imported and added to the __class_list
variable. This variable is used by the get_class_for() function to return
the correct source class for a given URL.
"""

import sys
import types

from . import (
    source_batoto,
    source_blogtruyenmoi,
    source_comixextra,
    source_kuaikanmanhua,
    source_mangadex,
    source_mangakakalot,
    source_manganato,
    source_mangasee,
    source_manhuaes,
    source_readcomiconline,
    source_thecomicseries,
    source_webtoons,
)
from .common_source import CommonSource

__class_list: list[type[CommonSource]] = []


def _get_all_source_modules() -> list[str]:
    """
    Return a list of all source modules.
    """
    out = list[str]()
    for _, val in globals().items():
        if isinstance(val, types.ModuleType) and val.__name__.startswith("mandown.sources.source_"):
            out.append(val.__name__)
    return out


for i in _get_all_source_modules():
    __class_list.append(sys.modules[i].get_class())


def get_class_for(url: str) -> type[CommonSource]:
    """
    Return a source that matches the URL.

    :raises ValueError: If no source matches the URL.
    """
    for c in __class_list:
        if c.check_url(url):
            return c
    raise ValueError("No sources found matched the URL query.")


def get_all_classes() -> list[type[CommonSource]]:
    """
    Return all imported source module classes. Best used for manual poking.
    """
    return __class_list
