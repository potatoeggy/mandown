from dataclasses import dataclass

from . import sources
from .base import BaseChapter, BaseMetadata


@dataclass
class Comic:
    def __init__(
        self,
        metadata: BaseMetadata,
        chapters: list[BaseChapter],
    ):
        self.metadata = metadata
        self.chapters = chapters
        self.source = sources.get_class_for(self.metadata.url)(self.metadata.url)

    def asdict(self) -> dict:
        return {
            "metadata": self.metadata.asdict(),
            "chapters": [c.asdict() for c in self.chapters],
        }

    def get_chapter_image_urls(self, chapter: BaseChapter) -> list[str]:
        return self.source.fetch_chapter_image_list(chapter)
