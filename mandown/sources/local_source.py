"""
Internal Mandown representation of local
persistent sources
"""

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from mandown.sources import get_class_for

from .base_source import BaseSource, Chapter, MangaMetadata

METADATA_PATH_NAME = "md-metadata.json"


class FileSystemChapterValidator(BaseModel):
    title: str
    url: str
    slug: str

    def to_discrete(self, source: BaseSource) -> Chapter:
        return Chapter(source, self.title, self.url)


class FileSystemMetadataValidator(BaseModel):
    title: str
    authors: list[str]
    url: str
    genres: list[str]
    description: str
    cover_art: str
    chapters: list[FileSystemChapterValidator]

    def to_discrete(self) -> MangaMetadata:
        return MangaMetadata(
            self.title,
            self.authors,
            self.url,
            self.genres,
            self.description,
            self.cover_art,
        )


class LocalSource:
    def __init__(
        self,
        path: Path | str,
        *,
        source: BaseSource | None = None,
        metadata: MangaMetadata | None = None,
        chapters: list[Chapter] | None = None,
        # TODO: generate image paths for each chapter
    ):
        """
        Attempt to open a new comic ready for writing.

        @param `path`: File path to open
        @param `create`: Create the file path if it does not exist
        @param `source` Use existing source if available (has priority over path)
        @param `metadata`: Use existing metadata if available (has priority over source)
        @param `chapters`: Use existing chapter data if available (has priority over source)
        """
        self.source = None
        self.metadata = None
        self.chapters = None

        path = Path(path)
        self.path = path

        # create the folder, failing gracefully
        # if the folder already exists
        path.mkdir(exist_ok=True)

        try:
            self._populate_from_path(path)
        except IOError as err:
            if source is metadata is chapters is None:
                raise IOError(
                    "Missing metadata file and no other metadata source specified."
                ) from err

        if source is not None:
            self.metadata = source.metadata
            self.chapters = source.chapters

        if metadata is not None:
            self.metadata = metadata

        if chapters is not None:
            self.chapters = chapters

        self.source = source or self.to_base_source()

    def _populate_from_path(self, path: Path) -> None:
        with open(path / METADATA_PATH_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        try:
            validated_data = FileSystemMetadataValidator(**data)
            self.metadata = validated_data
            self.source = self.to_base_source()  # spaghet everywhere
            self.chapters = [
                c.to_discrete(self.source) for c in validated_data.chapters
            ]
        except ValidationError as err:
            raise IOError("Improper metadata file") from err

    def save(self) -> None:
        data = dict(self.metadata.asdict())
        data["chapters"] = [
            {"title": c.title, "slug": c.slug, "url": c.url} for c in self.chapters
        ]

        with open(self.path / METADATA_PATH_NAME, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def to_base_source(self) -> BaseSource:
        if self.source:
            return self.source

        # god dammit
        source = get_class_for(self.metadata.url)(self.metadata.url)
        source._metadata = self.metadata
        source._chapters = self.chapters
        return source
