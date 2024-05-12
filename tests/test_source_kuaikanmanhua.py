from common import is_source_working, skip_in_ci

DESCRIPTION = "【KK原创投稿计划】\n亿万年前，在一片混沌之间忽然传出了一个细微的声响，那似乎是一声“喵...”，天地初创，神力蔓延，会有怎样一番景象？"


@skip_in_ci
def test_wuzhimao() -> None:
    return is_source_working(
        "https://www.kuaikanmanhua.com/web/topic/16222",
        title="五只猫",
        authors=["猫不错_"],
        genres=[],
        description=DESCRIPTION,
        cover_art="https://tn1-f2.kkmh.com/image/230209/wYPGM3UUB.webp-w750.jpg",
    )
