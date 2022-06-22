# pylint: disable=no-member,invalid-name,pointless-string-statement
"""
Generate mainwin.py while in mandown/ui/ with
`uic -g python -o mainwin.py form.ui`
"""
import sys

import requests
from mainwin import Ui_Widget
from PySide6.QtGui import QImage, QPixmap

import mandown
from mandown import iohandler
from mandown.comic import BaseComic

from PySide6.QtWidgets import (  # isort: skip
    QApplication,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)


COVER_IMG_HEIGHT = 400


class MandownQtUi(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.init_hooks()

        self.ui.progress_bar.setDisabled(True)
        self.ui.progress_bar.setValue(0)
        self.ui.label_progress.setText("")

        self.ui.label_metadata.setWordWrap(True)

        self.setWindowTitle("Mandown 0.10.0")

        self.source_path: str | None = None
        self.source_url: str | None = None
        self.dest_path: str | None = None
        self.chapters = None
        self._comic: BaseComic | None = None
        self.img_cover: QImage | None = None

        self.show()

    def init_hooks(self) -> None:
        # select "No" for default convert
        self.ui.radio_no_convert.toggle()
        # button: Open Folder
        self.ui.button_from_folder.clicked.connect(self.hook_from_folder)
        # button: Search URL
        self.ui.button_from_url.clicked.connect(self.hook_from_url)
        # button: Browse
        self.ui.pushButton_3.clicked.connect(self.hook_set_dest)
        # button: Start!
        self.ui.button_start.clicked.connect(self.hook_go)

    def metadata_to_table(self) -> list[str]:
        metadata = self.comic.metadata
        return [
            f"<b>Title:</b> {metadata.title}",
            f"<b>Author(s):</b> {', '.join(metadata.authors)}",
            f"<b>Genre(s):</b> {', '.join(metadata.genres)}",
            "",
            metadata.description,
        ]

    def chapters_to_table(self) -> list:
        # TODO: make them VIEWS / LAYOUTS not widgets
        # because i can't add checkboxes
        return [c.title for c in self.comic.chapters]

    @property
    def comic(self) -> BaseComic | None:
        return self._comic

    @comic.setter
    def comic(self, comic: BaseComic) -> None:
        self._comic = comic

        self.ui.label_metadata.setText("<br />".join(self.metadata_to_table()))

        for i, chap in enumerate(self.comic.chapters):
            self.ui.chapter_table.setItem(i, 0, QTableWidgetItem(""))
            self.ui.chapter_table.setItem(i, 1, QTableWidgetItem(chap.title))

        # refresh screen w/metadata et al here
        if comic.metadata.cover_art:
            r = requests.get(comic.metadata.cover_art)
            self.img_cover = QPixmap(
                QImage.fromData(r.content).scaledToHeight(COVER_IMG_HEIGHT)
            )
            self.ui.label_image.setPixmap(self.img_cover)

    """
    Hooks go here!
    """

    def hook_from_folder(self) -> None:
        # TODO: directly look for md-metadata.json instead
        self.source_path = QFileDialog.getExistingDirectory(
            self, "Open Comic Folder", "~"
        )
        self.ui.text_source.setText(self.source_path)
        self.ui.text_dest.setText(self.source_path)

        # load metadata
        try:
            self.comic = mandown.read(self.source_path)
        except FileNotFoundError:
            res = QMessageBox.critical(
                self,
                "Invalid Folder",
                "Folder is not a Mandown-created comic folder: Could not find md-metadata.json.",
                QMessageBox.Ok,
            )

    def hook_from_url(self) -> None:
        active_url = self.ui.text_source.text()
        try:
            comic = mandown.query(active_url)
        except ValueError:
            res = QMessageBox.critical(
                self,
                "Unknown Comic",
                "Could not find comic: URL did not match any sources.",
                QMessageBox.Ok,
            )
        self.comic = comic

    def hook_set_dest(self) -> None:
        self.dest_path = QFileDialog.getExistingDirectory(
            self, "Set Destination Folder", "~"
        )
        self.ui.text_dest.setText(self.dest_path)

    def hook_go(self) -> None:
        pass


def main() -> None:
    app = QApplication([])
    wid = MandownQtUi()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
