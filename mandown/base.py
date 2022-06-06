from dataclasses import dataclass

from slugify import slugify


@dataclass
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
    slug: str = ""

    def __post_init__(self) -> None:
        if not self.slug:
            self.slug = slugify(self.title)

    def asdict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "slug": self.slug,
        }
