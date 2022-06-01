import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from . import cbz, epub, pdf
from .base_converter import BaseConverter

CBZ = "cbz"
EPUB = "epub"
PDF = "pdf"


class ConvertFormats(str, Enum):
    # for typing purposes
    CBZ = "cbz"
    EPUB = "epub"
    PDF = "pdf"


@dataclass(kw_only=True)
class ConvertOptions:
    page_progression: Literal["ltr"] | Literal["rtl"] = "ltr"


def get_converter(convert_to: ConvertFormats) -> type[BaseConverter]:
    match convert_to:
        case ConvertFormats.CBZ:
            return cbz.CbzConverter
        case ConvertFormats.EPUB:
            return epub.EpubConverter
        case ConvertFormats.PDF:
            return pdf.PdfConverter
