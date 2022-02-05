import imghdr
from pathlib import Path

from PIL import Image


class Processor:
    def __init__(self, image_path: Path | str) -> None:
        self.image_path = Path(image_path)
        if not self.image_path.is_file() or imghdr.what(self.image_path) == "":
            raise ValueError(f"{self.image_path} does not lead to a valid image file")

        self.image = Image.open(self.image_path)
