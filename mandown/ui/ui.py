# pylint: disable=no-member
"""
Generate mainwin.py while in mandown/ui/ with
`uic -g python -o mainwin.py form.ui`
"""
import sys

from mainwin import Ui_Widget
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget


class QtUi(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.init_hooks()

        self.show()

        self.source_path: str | None = None
        self.source_url: str | None = None
        self.dest_path: str | None = None

    def init_hooks(self) -> None:
        self.ui.button_from_folder.clicked.connect(self.hook_from_folder)

    # hooks
    def hook_from_folder(self) -> None:
        self.source_path = QFileDialog.getExistingDirectory(
            self.base, "Open Comic Folder", "~"
        )
        self.ui.text_source.setText(self.source_path)
        # load metadata

    def hook_set_dest(self) -> None:
        self.dest_path = QFileDialog.getExistingDirectory(
            self, "Set Destination Folder", "~"
        )
        self.ui.text_dest.setText(self.dest_path)


def main() -> None:
    app = QApplication([])
    wid = QtUi()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
