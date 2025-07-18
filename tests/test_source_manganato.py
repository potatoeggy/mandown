from common import is_source_working, skip_in_ci

PUNPUN_DESCRIPTION = "Witness the titular Punpun - who is depicted as a tiny, caricatured bird in an otherwise normal human setting - as he copes with his dysfunctional family and friends, his love interest, his oncoming adolescence and his hyperactive mind."


@skip_in_ci
def test_punpun() -> None:
    return is_source_working(
        "https://www.natomanga.com/manga/oyasumi-punpun",
        title="Oyasumi Punpun",
        authors=["Asano Inio"],
        genres=["Comedy", "Drama", "Action", "Slice of life", "Seinen", "Psychological"],
        description=PUNPUN_DESCRIPTION,
        cover_art="https://imgs-2.2xstorage.com/thumb/oyasumi-punpun.webp",
    )
