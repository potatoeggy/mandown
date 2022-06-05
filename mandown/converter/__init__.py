from . import cbz, epub, pdf
from .base_converter import BaseConverter, ConvertFormats


def get_converter(convert_to: ConvertFormats) -> type[BaseConverter]:
    match convert_to:
        case ConvertFormats.CBZ:
            return cbz.CbzConverter
        case ConvertFormats.EPUB:
            return epub.EpubConverter
        case ConvertFormats.PDF:
            return pdf.PdfConverter
        case _:
            raise NotImplementedError(
                f"{convert_to} conversion has not been implemented yet!"
            )
