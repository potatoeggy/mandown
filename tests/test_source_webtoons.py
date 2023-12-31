from common import skip_in_ci

import mandown

BATMAN_DESCRIPTION = "Batman needs a break. But with new vigilante Duke Thomas moving into Wayne Manor and an endless supply of adopted, fostered, and biological superhero children to manage, Bruce Wayne is going to have his hands full. Being a father can't be harder than being Batman, right?"

REYN_DESCRIPTION = "Betrayal, hidden identities, family secrets. Left alone after her mother's murder, Reyn struggles to accept her wings, and searches for truth in a world that wants her dead. But the more she discovers, the more she begins to fear herself. Her brother has all the answers, but he disappears that same night. Can Reyn find him before the world discovers who she really is?  ~UP every Saturday 11AM EST~"


@skip_in_ci
def test_batman() -> None:
    batman_url = "https://www.webtoons.com/en/slice-of-life/batman-wayne-family-adventures/list?title_no=3180"
    comic = mandown.query(batman_url)

    expected_res = {
        "title": "Batman: Wayne Family Adventures",
        "authors": ["StarBite", "CRC Payne"],
        "genres": ["Slice of life"],
        "description": BATMAN_DESCRIPTION,
        "cover_art": "https://webtoon-phinf.pstatic.net/20210908_32/1631043278314jN45V_JPEG/3BatmanFamilyAdven_desktop_thumbnail.jpg?type=a306",
        "url": batman_url,
    }

    assert comic.metadata.asdict() == expected_res
    assert comic.chapters


@skip_in_ci
def test_reyn() -> None:
    # test canvas
    reyn_url = "https://www.webtoons.com/en/challenge/reyn-angel-of-freedom/list?title_no=423104"

    comic = mandown.query(reyn_url)

    expected_res = {
        "title": "Reyn: Angel of Freedom",
        "authors": ["erlance"],
        "genres": ["Supernatural", "Drama"],
        "description": REYN_DESCRIPTION,
        "cover_art": "https://webtoon-phinf.pstatic.net/20230703_36/1688394256514spH74_JPEG/20f96dd9-008b-4fe9-bf68-4b6ed37e49f12435456437735264238.jpeg",
        "url": reyn_url,
    }

    assert comic.metadata.asdict() == expected_res
    assert comic.chapters

    first_chapter = comic.get_chapter_image_urls(comic.chapters[0])
    assert first_chapter
