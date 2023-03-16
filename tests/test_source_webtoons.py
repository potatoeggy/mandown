import mandown

BATMAN_DESCRIPTION = "Batman needs a break. But with new vigilante Duke Thomas moving into Wayne Manor and an endless supply of adopted, fostered, and biological superhero children to manage, Bruce Wayne is going to have his hands full. Being a father can't be harder than being Batman, right?"


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
