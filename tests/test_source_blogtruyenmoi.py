from common import skip_in_ci, is_source_working

URL = "https://blogtruyenmoi.com/9600/kobayashi-san-chi-no-maid-dragon"
REDUCED_URL = "https://blogtruyenmoi.com/9600"
COVER_URL = (
    "https://i7.xem-truyen.com/manga/9/9600/834dff95-65b3-46ed-be59-b246a5663b1b.thumb_500x.jpg"
)
DESCRIPTION = "truyện kể về nhân vật Kobayashi - một nữ kĩ sư phần mềm sống một mình ở một khu chung cư. Trong một lần say tí bỉ, cô tình cờ cứu giúp một con rồng tên là Tooru. Có nợ thì phải trả, cô rồng Tooru quyết tâm sẽ giúp đỡ ân nhân của mình dưới vai trò là một hầu gái."


@skip_in_ci
def test_kobayashi() -> None:
    return is_source_working(
        URL,
        title="Kobayashi-san Chi no Maid Dragon",
        authors=["Cool Kyoushinja"],
        genres=[
            "Comedy",
            "Seinen",
            "Slice of life",
            "Ecchi",
            "Drama",
            "Fantasy",
            "Yuri",
        ],
        description=DESCRIPTION,
        cover_art=COVER_URL,
        refined_url=REDUCED_URL,
    )
