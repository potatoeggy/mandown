from .base_converter import BaseConverter


class EpubConverter(BaseConverter):
    pass


def get_class() -> EpubConverter:
    return EpubConverter
