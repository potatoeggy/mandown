from common import is_source_working, skip_in_ci

URL = "https://www.mangago.me/read-manga/unordinary"
COVER_URL = "https://i2.mangapicgallery.com/r/coverlink/rUROHYYKHa8HiXPW8mnateWZ0_YjIwluoIysk81cAyFYX7_sQPoWCy9XCNBIGMAL0P4XAUguSYcdtBBW4_0.jpg?4"
DESCRIPTION = "The world is not perfect. Learning to deal with its flaws is just a normal part of life. But there comes a point where these imperfections spawn a crushing realization... that something needs to change..."


@skip_in_ci
def test_unordinary() -> None:
    return is_source_working(
        URL,
        title="Unordinary",
        authors=["Uru-chan"],
        genres=["Fantasy", "Drama", "Tragedy"],
        description=DESCRIPTION,
        cover_art=COVER_URL,
    )
