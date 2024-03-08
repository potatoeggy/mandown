from common import is_source_working, skip_in_ci

BEHEMOTH_DESCRIPTION = """Greyson's world is crumbling following his brother's sudden and mysterious death...
His sleepless nights are haunted by vivid nightmares of a terrifying monster, pushing him to the brink of losing both his sanity and his job as a social worker. But he's truly shaken to the core when his newest case -- a young orphaned girl named Wren -- is found at the scene of a brutal murder, just hours after first meeting Greyson. The line between nightmare and waking life blurs as Greyson soon discovers that the monster from his dreams might just be real -- a mythical, ancient beast that is bringing about the end of the world, with shocking connections to both him and Wren..."""


@skip_in_ci
def test_behemoth() -> None:
    return is_source_working(
        "https://readcomiconline.li/Comic/Behold-Behemoth",
        title="Behold, Behemoth",
        authors=["Tate Brombal"],
        genres=["Mystery"],
        description=BEHEMOTH_DESCRIPTION,
        cover_art="https://readcomiconline.li/Uploads/Etc/11-3-2022/3912564307190.jpg",
    )
