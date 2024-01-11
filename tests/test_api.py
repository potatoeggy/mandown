from pathlib import Path

import mandown
from mandown import BaseChapter, BaseComic, BaseMetadata


def test_load_save(tmp_path: Path) -> None:
    comic = BaseComic(
        BaseMetadata(
            title="Test Comic",
            authors=["Test Author"],
            url="",
            genres=["Test", "Genres"],
            description="Test Description",
            cover_art="https://example.com/cover.jpg",
        ),
        [
            BaseChapter("Test Chapter", "https://example.com/chapter"),
        ],
    )
    mandown.save_metadata(comic, tmp_path)
    loaded = mandown.load(tmp_path)
    assert comic.asdict() == loaded.asdict()
