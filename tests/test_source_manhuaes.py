from common import skip_in_ci, is_source_working

DESCRIPTION = "This is the story of Song Woo Mun. The village Inn owner’s son, Song Woo Mun is weak as a young boy, whose condition only when he suffers a loss of his intellect, due to the Sansu-hwa, a painting gifted by a Sage. But unbeknownst to everyone, his life is about to change, and a new destiny awaits him, when he turns 20. Not only does he undergo an awakening, but he also sees the Undefeatable Flower blooming in the painting. What could all of this mean for Woo Mun? And what strange world awaits him?"


@skip_in_ci
def test_undefeatable() -> None:
    return is_source_working(
        "https://manhuaes.com/manga/the-undefeatable-swordsman",
        title="The Undefeatable Swordsman",
        authors=["TUS"],
        genres=["Action", "Adventure", "Fantasy"],
        description=DESCRIPTION,
        cover_art="https://manhuaaz.com/wp-content/uploads/2023/03/the-undefeatable-swordsman-193x278.jpg",
        refined_url="https://manhuaaz.com/manga/the-undefeatable-swordsman",
    )
