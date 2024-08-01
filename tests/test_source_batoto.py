from common import is_source_working, skip_in_ci

URL = "https://bato.to/title/148152-calvin-hobbes"
COVER_URL = "https://xfs-n02.xfsbb.com/thumb/W600/ampi/338/338d61287365ec7247ce40b729ebf7de865862fc_474_503_48513.jpeg"
DESCRIPTION = "Calvin and Hobbes follows the humorous antics of the title characters: Calvin, a precocious, mischievous, and adventurous six-year-old boy; and Hobbes, his sardonic stuffed tiger. Set in the suburban United States of the 1980s and 1990s, the strip depicts Calvin's frequent flights of fancy and friendship with Hobbes. It also examines Calvin's relationships with his long-suffering parents and with his classmates, especially his neighbor Susie Derkins. Hobbes's dual nature is a defining motif for the strip: to Calvin, Hobbes is a living anthropomorphic tiger, while all the other characters seem to see Hobbes as an inanimate stuffed toy\u00e2\u0080\u0094though Watterson has not clarified exactly how Hobbes is perceived by others. Though the series does not frequently mention specific political figures or ongoing events, it does explore broad issues like environmentalism, public education, and philosophical quandaries"


@skip_in_ci
def test_calvinhobbes() -> None:
    return is_source_working(
        URL,
        title="Calvin & Hobbes",
        authors=["Bill Watterson"],
        genres=["Comic", "Kodomo", "Shoujo", "Shounen", "Comedy", "Kids", "Slice of Life"],
        description=DESCRIPTION,
        cover_art=COVER_URL,
    )
