from common import is_source_working, skip_in_ci

URL = "https://comixextra.com/comic/betty-and-veronica-double-digest"
COVER_URL = "https://1.bp.blogspot.com/-oaMrKlTMYZI/X4Ops8iz62I/AAAAAAAAlM0/qyDYDW38wuYiV7Nz038hfJxGcTwNi5zNwCLcBGAsYHQ/s0/Betty%2Band%2BVeronica%2BDouble%2BDigest-min.jpg"
DESCRIPTION = "Nothing''s better than 100+ pages of laughs and love triangles! Read some of the best stories from best frenemies Betty and Veronica!"


@skip_in_ci
def test_bettyveronica() -> None:
    return is_source_working(
        URL,
        title="Betty and Veronica Double Digest",
        authors=["Various"],
        genres=[
            "Romance",
        ],
        description=DESCRIPTION,
        cover_art=COVER_URL,
    )
