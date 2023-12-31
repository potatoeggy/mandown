from common import skip_in_ci

import mandown

PUNPUN_DESCRIPTION = "Witness the titular Punpun - who is depicted as a tiny, caricatured bird in an otherwise normal human setting - as he copes with his dysfunctional family and friends, his love interest, his oncoming adolescence and his hyperactive mind."


@skip_in_ci
def test_punpun() -> None:
    punpun_url = "https://chapmanganato.com/manga-fa957135"

    comic = mandown.query(punpun_url)

    expected_res = {
        "title": "Oyasumi Punpun",
        "authors": ["Asano Inio"],
        "genres": [
            "Action",
            "Comedy",
            "Drama",
            "Psychological",
            "Seinen",
            "Slice of life",
        ],
        "description": PUNPUN_DESCRIPTION,
        "cover_art": "https://avt.mkklcdnv6temp.com/36/c/4-1583471170.jpg",
        "url": punpun_url,
    }

    assert comic.metadata.asdict() == expected_res
    assert comic.chapters

    first_chapter = comic.get_chapter_image_urls(comic.chapters[0])
    assert first_chapter
