import mandown

comic = mandown.query("https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To")

mandown.download(comic, ".", end=3)
