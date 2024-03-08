from . import sources
from .base import BaseChapter, BaseMetadata
from .sources.base_source import BaseSource


class BaseComic:
    """
    A comic with metadata and chapter data.

    :param `metadata`: Metadata of the comic
    :param `chapters`: A list of chapters of the comic
    """

    def __init__(
        self,
        metadata: BaseMetadata,
        chapters: list[BaseChapter],
    ):
        self.metadata = metadata
        self.chapters = chapters
        try:
            self.source = sources.get_class_for(self.metadata.url)(self.metadata.url)
        except ValueError as err:
            if self.metadata.url == "":  # sentinel value
                self.source = BaseSource("")
            else:
                raise ValueError from err

    def asdict(self) -> dict:
        """
        Return a dictionary representation of the comic.
        """

        return {
            "metadata": self.metadata.asdict(),
            "chapters": [c.asdict() for c in self.chapters],
        }

    def get_chapter_image_urls(self, chapter: BaseChapter) -> list[str]:
        """
        Fetch a list of image URLs of a chapter based on the
        current source.

        :param `chapter`: The chapter to fetch
        :return: A list of image URLs
        """
        return self.source.fetch_chapter_image_list(chapter)

    def set_chapter_range(self, *, start: int | None = None, end: int | None = None) -> None:
        """
        `start` and `end` are zero-indexed.

        :param `start`: The index of the first chapter to keep
        :param `end`: The index of the last chapter to keep (exclusive)
        """
        self.chapters = self.chapters[start:end]

    def update(self, *, chapters: bool = True, metadata: bool = True) -> None:
        """
        Refresh comic.metadata and comic.chapters with new information
        from the source. Remember to call mandown.save_metadata(comic)
        to actually save the updated data to the filesystem.

        :param `chapters`: whether to update the chapter index
        :param `metadata`: whether to update comic metadata
        """
        if chapters:
            self.chapters = self.source.fetch_chapter_list()

        if metadata:
            self.metadata = self.source.fetch_metadata()

    def __str__(self) -> str:
        return f"""
Title: {self.metadata.title},
Author(s): {', '.join(self.metadata.authors)}
URL: {self.metadata.url}
Genres: {', '.join(self.metadata.genres)}
Chapters: {len(self.chapters)}
Description:
    {self.metadata.description}
""".strip()
