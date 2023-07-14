from common import skip_in_ci

import mandown

URL = "https://mangadex.org/title/a3d681d7-a239-45a9-8446-5bfc61ca48fa"
COVER_URL = "https://uploads.mangadex.org/covers/a3d681d7-a239-45a9-8446-5bfc61ca48fa/f6c8523e-cc60-410a-8709-99fd3020c6e3.jpg"
DESCRIPTION = "Satoshi, a 16-year-old first year high school student just got a part time job as a housekeeper for a mansion surrounded by roses. A girl called Shizu lives there, who appears innocent and pure but lives haphazardly. However, there seems to be a mystery surrounding her: who is the other girl that looks at Satoshi with a cold blank stare?"


@skip_in_ci
def test_ibarahime() -> None:
    comic = mandown.query(URL)

    expected_res = {
        "title": "Good Morning, Sleeping Beauty",
        "authors": ["Megumi Morino"],
        "genres": [
            "Psychological",
            "Romance",
            "Comedy",
            "Drama",
            "Slice of Life",
        ],
        "description": DESCRIPTION,
        "cover_art": COVER_URL,
        "url": URL,
    }

    assert comic.metadata.asdict() == expected_res
    assert comic.chapters
