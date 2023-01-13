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
