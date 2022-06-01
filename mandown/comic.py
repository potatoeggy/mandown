from dataclasses import dataclass, field
from pathlib import Path

from slugify import slugify

from . import iohandler, sources


@dataclass(frozen=True)
class BaseMetadata:
    title: str
    authors: list[str]
    url: str
    genres: list[str]
    description: str
    cover_art: str

    def __post_init__(self) -> None:
        self.title_slug = slugify(self.title)

    def asdict(self) -> dict:
        return {
            "title": self.title,
            "authors": self.authors,
            "url": self.url,
            "genres": self.genres,
            "description": self.description,
            "cover_art": self.cover_art,
        }


@dataclass
class BaseChapter:
    title: str
    url: str
    slug: str = None

    def __post_init__(self) -> None:
        if self.slug is None:
            self.slug = slugify(self.title)

    def asdict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "slug": self.slug,
        }


@dataclass
class ComicChapter(BaseChapter):
    _images: list[str] = field(init=False, default_factory=list)

    @property
    def images(self) -> list[str]:
        if self._images:
            return self.images

        self._images = 0


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

    def save_metadata(self, path: Path | str) -> None:
        iohandler.save_comic(self, path)
