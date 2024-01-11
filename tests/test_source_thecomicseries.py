from common import skip_in_ci, is_source_working

DESCRIPTION = "Several heroes rose and fell without much attention and this is where their stories are woven together. Most of the characters in this series are in the public domain but the stories and depictions are original."


@skip_in_ci
def test_retcon() -> None:
    return is_source_working(
        "https://comicfury.com/comicprofile.php?url=retcon",
        title="Retcon",
        authors=["Nicholas Ivan Ladendorf"],
        genres=[
            "Action",
            "Science Fiction",
            "Adventure",
            "Super Hero",
            "Golden Age",
            "Public Domain",
        ],
        description=DESCRIPTION,
        cover_art="https://comicfury.com/comicavatars/275/56926_1487018262.png",
    )
