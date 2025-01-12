class MandownError(Exception):
    pass


class NoImagesFoundError(MandownError):
    pass


class ImageDownloadError(MandownError):
    pass


class ChapterImageCountMismatchError(MandownError):
    pass
