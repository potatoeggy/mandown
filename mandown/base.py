from dataclasses import dataclass

from comicon import SLUGIFY_ARGS
from slugify import slugify


@dataclass(slots=True)
class BaseMetadata:
    """
    Metadata for a comic.

    :param `title`: The title of the comic
    :param `authors`: A list of authors of the comic
    :param `url`: The URL of the comic
    :param `genres`: A list of genres of the comic
    :param `description`: A description of the comic
    :param `cover_art`: The URL of the cover art
    :param `title_slug`: The slug of the title
    """

    title: str
    authors: list[str]
    url: str
    genres: list[str]
    description: str
    cover_art: str
    title_slug: str = ""

    def __post_init__(self) -> None:
        self.title_slug = slugify(self.title, **SLUGIFY_ARGS).strip()

    def asdict(self) -> dict[str, str | list[str]]:
        """
        Return a dictionary representation of the metadata.
        """

        return {
            "title": self.title,
            "authors": self.authors,
            "url": self.url,
            "genres": self.genres,
            "description": self.description,
            "cover_art": self.cover_art,
        }


@dataclass(slots=True)
class BaseChapter:
    """
    A chapter of a comic.

    :param `title`: The title of the chapter
    :param `url`: The URL of the chapter
    :param `slug`: The slug of the chapter
    """

    title: str
    url: str
    slug: str = ""

    def __post_init__(self) -> None:
        if not self.slug:
            self.slug = slugify(self.title, **SLUGIFY_ARGS).strip()

    def asdict(self) -> dict:
        """
        Return a dictionary representation of the chapter.
        """
        return {
            "title": self.title,
            "url": self.url,
            "slug": self.slug,
        }

    @staticmethod
    def sync_slug_order(
        chapters: list["BaseChapter"],
    ) -> None:
        """
        Given a list of chapters, prefix their slugs with their index in the list if they are not
        already sorted. This is useful for sorting chapters in a comic.
        """
        if sorted(chapters, key=lambda c: c.slug) == chapters:
            # already sorted, no need to prefix
            print("sorted")
            return
        for i, chapter in enumerate(chapters, start=1):
            chapter.slug = f"{i:05}-{chapter.slug}"
