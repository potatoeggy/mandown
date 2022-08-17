from .api import (  # isort: skip
    convert,
    convert_progress,
    download,
    download_progress,
    load,
    process,
    process_progress,
    query,
)

# stupid pylance deleting my imports
# pylint: disable=pointless-statement
(
    convert,
    convert_progress,
    download,
    download_progress,
    load,
    process,
    process_progress,
    query,
)

__version__ = (1, 0, 1)
__version_str__ = ".".join(map(str, __version__))
