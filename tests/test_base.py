import pytest

import mandown


def test_basemetadata() -> None:
    title = "Test title"
    authors = ["Test author", "Test author 2"]
    url = "https://example.com"
    genres = ["Test genre", "Test genre 2"]
    description = "Test description"
    cover_art = "https://example.com/cover.jpg"
    title_slug = "test-title"

    metadata = mandown.BaseMetadata(
        title=title,
        authors=authors,
        url=url,
        genres=genres,
        description=description,
        cover_art=cover_art,
    )

    assert metadata.asdict() == {
        "title": title,
        "authors": authors,
        "url": url,
        "genres": genres,
        "description": description,
        "cover_art": cover_art,
    }
    assert metadata.title_slug == title_slug


def test_basechapter() -> None:
    title = "Test title"
    url = "https://example.com"
    slug = "test-title"

    chapter = mandown.BaseChapter(title=title, url=url)

    assert chapter.asdict() == {"title": title, "url": url, "slug": slug}


def test_basecomic() -> None:
    title = "Test title"
    authors = []
    url = "https://example.com"
    genres = []
    description = "Test description"
    cover_art = "https://example.com/cover.jpg"

    metadata = mandown.BaseMetadata(
        title=title,
        authors=authors,
        url=url,
        genres=genres,
        description=description,
        cover_art=cover_art,
    )

    with pytest.raises(ValueError):
        mandown.BaseComic(metadata=metadata, chapters=[])

    sentinel_url = ""
    metadata = mandown.BaseMetadata(
        title=title,
        authors=authors,
        url=sentinel_url,
        genres=genres,
        description=description,
        cover_art=cover_art,
    )

    chapters = [
        mandown.BaseChapter(title=f"Test chapter {i}", url="https://example.com")
        for i in range(10)
    ]

    comic = mandown.BaseComic(metadata=metadata, chapters=chapters)
    assert comic.asdict() == {
        "metadata": metadata.asdict(),
        "chapters": [c.asdict() for c in chapters],
    }

    comic.set_chapter_range(start=0, end=5)
    assert comic.asdict() == {
        "metadata": metadata.asdict(),
        "chapters": [c.asdict() for c in chapters[:6]],
    }
