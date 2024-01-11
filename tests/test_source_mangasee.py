from common import skip_in_ci, is_source_working

KAGUYA_DESCRIPTION = "Kaguya Shinomiya and Miyuki Shirogane are the members of the incredibly prestigious Shuichi'in Academy's student council, asserting their positions as geniuses among geniuses. All the time they spend together has caused the two of them to develop feelings for each other, but their pride will not allow them to be the one to confess and become the submissive one in the relationship! Love is war, and their battle to make the other confess begins now!"


@skip_in_ci
def test_kaguya() -> None:
    return is_source_working(
        "https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To",
        title="Kaguya-sama - Love Is War",
        authors=["AKASAKA Aka"],
        genres=[
            "Comedy",
            "Drama",
            "Romance",
            "School Life",
            "Seinen",
            "Slice of Life",
        ],
        description=KAGUYA_DESCRIPTION,
        cover_art="https://temp.compsci88.com/cover/Kaguya-Wants-To-Be-Confessed-To.jpg",
    )
