from ..base import BaseChapter, BaseMetadata


class BaseSource:
    name = "Source name goes here"
    domains = ["Source domains goes here"]
    headers: dict[str, str] = {}

    _metadata: BaseMetadata | None = None
    _chapters: list[BaseChapter] = []

    def __init__(self, url: str):
        """
        An object representing network state for fetching data of a comic.
        """
        self.url = url

    @property
    def metadata(self) -> BaseMetadata:
        if self._metadata:
            return self._metadata
        self._metadata = self.fetch_metadata()
        return self._metadata

    @property
    def chapters(self) -> list[BaseChapter]:
        if self._chapters:
            return self._chapters
        self._chapters = self.fetch_chapter_list()
        return self._chapters

    def fetch_metadata(self) -> BaseMetadata:
        """
        Fetch and return title, author, and url of the comic.
        """
        raise NotImplementedError("Metadata getter not overridden")

    def fetch_chapter_list(self) -> list[BaseChapter]:
        """
        Fetch and return a list of chapter titles and their URL in ascending order.
        """
        raise NotImplementedError("Chapter list getter not overridden")

    def fetch_chapter_image_list(self, chapter: BaseChapter) -> list[str]:
        """
        Given a chapter link, fetch and return a list of image URLs in ascending
        order for that chapter.
        """
        raise NotImplementedError("Image URL getter not overridden")

    @staticmethod
    def check_url(url: str) -> bool:
        """
        Returns whether the url given matches that of the site and is processable
        """
        raise NotImplementedError("URL checker not overridden")


def get_class() -> type[BaseSource]:
    return BaseSource
