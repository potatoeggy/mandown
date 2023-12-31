from common import skip_in_ci

import mandown

KAGUYA_DESCRIPTION = "Kaguya Shinomiya and Miyuki Shirogane are the members of the incredibly prestigious Shuichi'in Academy's student council, asserting their positions as geniuses among geniuses. All the time they spend together has caused the two of them to develop feelings for each other, but their pride will not allow them to be the one to confess and become the submissive one in the relationship! Love is war, and their battle to make the other confess begins now!"


@skip_in_ci
def test_kaguya() -> None:
    kaguya_url = "https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To"

    comic = mandown.query(kaguya_url)

    expected_res = {
        "title": "Kaguya-sama - Love Is War",
        "authors": ["AKASAKA Aka"],
        "genres": [
            "Comedy",
            "Drama",
            "Romance",
            "School Life",
            "Seinen",
            "Slice of Life",
        ],
        "description": KAGUYA_DESCRIPTION,
        "cover_art": "https://temp.compsci88.com/cover/Kaguya-Wants-To-Be-Confessed-To.jpg",
        "url": kaguya_url,
    }

    assert comic.metadata.asdict() == expected_res
    assert comic.chapters

    first_chapter = comic.get_chapter_image_urls(comic.chapters[0])
    assert first_chapter
