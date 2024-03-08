# pylint: disable=no-member,invalid-name,pointless-string-statement
"""
Generate mainwin.py while in mandown/ui/ with
`uic -g python -o mainwin.py form.ui`
"""

import sys
from pathlib import Path

import requests
from PySide6.QtGui import QImage, QPixmap

import mandown

from .. import __version_str__
from ..comic import BaseComic
from .mainwin import Ui_Widget

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
        self.ui.label_progress.setText("Waiting")

        self.ui.label_metadata.setWordWrap(True)

        self.setWindowTitle(f"Mandown {__version_str__}")

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
            self.img_cover = QPixmap(QImage.fromData(r.content).scaledToHeight(COVER_IMG_HEIGHT))
            self.ui.label_image.setPixmap(self.img_cover)

    @property
    def text_dest_full(self) -> str:
        return str(Path(self.ui.text_dest.text()) / self.comic.metadata.title)

    """
    Hooks go here!
    """

    def hook_from_folder(self) -> None:
        # TODO: directly look for md-metadata.json instead
        self.source_path = QFileDialog.getExistingDirectory(self, "Open Comic Folder", "~")
        self.ui.text_source.setText(self.source_path)
        self.ui.text_dest.setText(str(Path(self.source_path).parent))

        # load metadata
        try:
            self.comic = mandown.load(self.source_path)
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
        self.dest_path = QFileDialog.getExistingDirectory(self, "Set Destination Folder", "~")
        self.ui.text_dest.setText(self.dest_path)

    def hook_go(self) -> None:
        if not self.ui.text_source.text():
            # if empty
            res = QMessageBox.critical(
                self,
                "Missing source",
                "Please select a source folder or URL",
                QMessageBox.Ok,
            )

        if not self.ui.text_dest.text():
            # if empty
            res = QMessageBox.critical(
                self,
                "Missing destination",
                "Please select a destination directory.",
                QMessageBox.Ok,
            )
            return

        if not self.comic:
            res = QMessageBox.critical(
                self,
                "Something went wrong",
                "ERROR: if not self.comic check failed. You should never see this message.",
            )
            return

        # heavy bits
        self.ui.label_progress.setText("Downloading")
        max_size = len(self.comic.chapters)
        self.ui.progress_bar.setDisabled(False)
        for i, _ in enumerate(
            mandown.download_progress(
                self.comic,
                self.ui.text_dest.text(),
                threads=4,
            ),
            start=1,
        ):
            # TODO: this hangs the program so move it to a QThread
            self.ui.progress_bar.setValue(int(i / max_size * 100))

        # convert
        if not self.ui.radio_no_convert.isChecked():
            target = "none"
            if self.ui.radio_convert_cbz.isChecked():
                target = "cbz"
            elif self.ui.radio_convert_epub.isChecked():
                target = "epub"
            elif self.ui.radio_convert_pdf.isChecked():
                target = "pdf"

            self.ui.label_progress.setText("Converting")
            self.ui.progress_bar.setValue(1)
            for i, text in enumerate(
                mandown.convert_progress(
                    self.comic,
                    self.text_dest_full,
                    target,
                    self.text_dest_full,
                ),
                start=1,
            ):
                self.ui.label_progress.setText(text)
                self.ui.progress_bar.setValue(int(i / max_size * 100))

        res = QMessageBox.information(self, "Done", "All operations complete.", QMessageBox.Ok)

        self.ui.progress_bar.setDisabled(True)


def main() -> None:
    app = QApplication([])
    wid = MandownQtUi()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
