import mandown
from mandown.processor import ProcessOps

comic = mandown.query("https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To")

mandown.download(comic, ".", end=3)
print("procesing")
mandown.process(f"./{comic.metadata.title}", ops=[ProcessOps.SPLIT_DOUBLE_PAGES])
