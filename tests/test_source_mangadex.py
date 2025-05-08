from common import is_source_working, skip_in_ci

DESCRIPTION = """All’s fair when love is war!

Two geniuses. Two brains. Two hearts. One battle. Who will confess their love first…?!

Kaguya Shinomiya and Miyuki Shirogane are two geniuses who stand atop their prestigious academy’s student council, making them the elite among elite. But it’s lonely at the top and each has fallen for the other. There’s just one huge problem standing in the way of lovey-dovey bliss—they’re both too prideful to be the first to confess their romantic feelings and thus become the “loser” in the competition of love! And so begins their daily schemes to force the other to confess first!"""


@skip_in_ci
def test_kaguya_mangadex() -> None:
    return is_source_working(
        "https://mangadex.org/title/37f5cce0-8070-4ada-96e5-fa24b1bd4ff9",
        title="Kaguya-sama: Love Is War",
        authors=["Akasaka Aka"],
        genres=[
            "Romance",
            "Comedy",
            "Drama",
            "School Life",
            "Slice of Life",
        ],
        description=DESCRIPTION,
        cover_art="https://uploads.mangadex.org/covers/37f5cce0-8070-4ada-96e5-fa24b1bd4ff9/e21ca520-5054-4041-a07e-de8b7c683522.jpg",
    )
