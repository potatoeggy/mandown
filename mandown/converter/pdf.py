from .base_converter import BaseConverter


class PdfConverter(BaseConverter):
    pass


def get_class() -> PdfConverter:
    return PdfConverter
