import typer

app = typer.Typer()


@app.command()
def hello(name: str) -> None:
    typer.echo(f"Hello {name}")


if __name__ == "__main__":
    # app()

    import mangadownloader
    from mangadownloader.sources.source_mangasee import MangaSeeSource

    kag = MangaSeeSource("https://mangasee123.com/manga/Grand-Blue")
    chapters = kag.get_chapter_list()
    first_chap = kag.get_chapter_image_list(chapters[0])
    mangadownloader.download_chapter(first_chap, "/media/kag")
