import os

import pytest

import mandown

skip_in_ci = pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true", reason="Do not run network tests in CI"
)


def is_source_working(
    url: str,
    /,
    *,
    title: str,
    authors: list[str],
    genres: list[str],
    description: str,
    cover_art: str,
    refined_url: str | None = None,
) -> None:
    expected_res = {
        "title": title,
        "authors": authors,
        "genres": genres,
        "description": description,
        "cover_art": cover_art,
        "url": refined_url or url,
    }
    comic = mandown.query(url)

    assert (
        comic.metadata.asdict() == expected_res
    ), f"Expected:\n{expected_res}\n\nGot:\n{comic.metadata.asdict()}"
    assert comic.chapters, "Comic should have chapters"

    first_chapter = comic.get_chapter_image_urls(comic.chapters[0])
    assert first_chapter, "First chapter should have images"
