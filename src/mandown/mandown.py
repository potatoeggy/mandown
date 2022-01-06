import os
from mandown import sources, iohandler
from mandown.sources.base_source import BaseSource


def query(url: str) -> BaseSource:
    """
    Return the metadata and chapter list for a URL.
    """
    source: BaseSource = sources.get_class_for(url)(url)
    source.get_metadata()
    source.get_chapter_list()
    print("Found story:")
    print(source)
    return source


def download(
    url: str,
    dest_folder: str = os.getcwd(),
    start_chapter: int | None = None,
    end_chapter: int | None = None,
    maxthreads: int = 1,
) -> None:
    """
    Download from a URL chapters start_chapter to end_chapter.
    Defaults to the first chapter and last chapter, respectively
    in the working directory.
    """
    if not os.path.isdir(dest_folder):
        raise ValueError(f"{dest_folder} is not a valid folder path.")

    source: BaseSource = query(url)

    # starting to think that immutability is much better than whatever
    # the heck is going on here
    target_path = os.path.join(dest_folder, source.get_metadata().title)
    if not os.path.isdir(target_path):
        os.mkdir(target_path)

    # if they are undefined
    start_chapter = start_chapter or 1
    end_chapter = end_chapter or len(source.get_chapter_list())

    # zero-index
    start_chapter -= 1

    for i, chapter in enumerate(source.get_chapter_list()[start_chapter:end_chapter]):
        print(
            f"Downloading {chapter.title} ({i+1}/{len(source.get_chapter_list())})..."
        )
        images = source.get_chapter_image_list(chapter)
        iohandler.download_chapter(images, target_path, maxthreads)
    print("Done.")
