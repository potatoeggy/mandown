# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 5.15.4
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName("Widget")
        Widget.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(Widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QLabel(Widget)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.text_source = QLineEdit(Widget)
        self.text_source.setObjectName("text_source")

        self.horizontalLayout_2.addWidget(self.text_source)

        self.button_from_url = QPushButton(Widget)
        self.button_from_url.setObjectName("button_from_url")
        icon = QIcon(QIcon.fromTheme("search"))
        self.button_from_url.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.button_from_url)

        self.button_from_folder = QPushButton(Widget)
        self.button_from_folder.setObjectName("button_from_folder")
        icon1 = QIcon(QIcon.fromTheme("folder"))
        self.button_from_folder.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.button_from_folder)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QLabel(Widget)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.text_dest = QLineEdit(Widget)
        self.text_dest.setObjectName("text_dest")

        self.horizontalLayout_4.addWidget(self.text_dest)

        self.pushButton_3 = QPushButton(Widget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.pushButton_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName("label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.label_image = QLabel(Widget)
        self.label_image.setObjectName("label_image")

        self.verticalLayout.addWidget(self.label_image)

        self.label_metadata = QLabel(Widget)
        self.label_metadata.setObjectName("label_metadata")

        self.verticalLayout.addWidget(self.label_metadata)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QLabel(Widget)
        self.label.setObjectName("label")

        self.verticalLayout_4.addWidget(self.label)

        self.chapter_table = QTableWidget(Widget)
        self.chapter_table.setObjectName("chapter_table")

        self.verticalLayout_4.addWidget(self.chapter_table)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QLabel(Widget)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.radio_no_convert = QRadioButton(Widget)
        self.radio_no_convert.setObjectName("radio_no_convert")

        self.horizontalLayout_3.addWidget(self.radio_no_convert)

        self.radio_convert_epub = QRadioButton(Widget)
        self.radio_convert_epub.setObjectName("radio_convert_epub")

        self.horizontalLayout_3.addWidget(self.radio_convert_epub)

        self.radio_convert_pdf = QRadioButton(Widget)
        self.radio_convert_pdf.setObjectName("radio_convert_pdf")

        self.horizontalLayout_3.addWidget(self.radio_convert_pdf)

        self.radio_convert_cbz = QRadioButton(Widget)
        self.radio_convert_cbz.setObjectName("radio_convert_cbz")

        self.horizontalLayout_3.addWidget(self.radio_convert_cbz)

        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_progress = QLabel(Widget)
        self.label_progress.setObjectName("label_progress")

        self.horizontalLayout_5.addWidget(self.label_progress)

        self.progress_bar = QProgressBar(Widget)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setValue(24)

        self.horizontalLayout_5.addWidget(self.progress_bar)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.button_start = QPushButton(Widget)
        self.button_start.setObjectName("button_start")

        self.verticalLayout_2.addWidget(self.button_start)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)

    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", "Widget", None))
        self.label_4.setText(QCoreApplication.translate("Widget", "Source Folder / URL:", None))
        self.button_from_url.setText(QCoreApplication.translate("Widget", "Search URL", None))
        self.button_from_folder.setText(QCoreApplication.translate("Widget", "Open Folder", None))
        self.label_5.setText(QCoreApplication.translate("Widget", "Save to:", None))
        self.pushButton_3.setText(QCoreApplication.translate("Widget", "Browse", None))
        self.label_2.setText(QCoreApplication.translate("Widget", "Metadata", None))
        self.label.setText(QCoreApplication.translate("Widget", "Chapters", None))
        self.label_3.setText(QCoreApplication.translate("Widget", "Convert?", None))
        self.radio_no_convert.setText(QCoreApplication.translate("Widget", "No", None))
        self.radio_convert_epub.setText(QCoreApplication.translate("Widget", "EPUB", None))
        self.radio_convert_pdf.setText(QCoreApplication.translate("Widget", "PDF", None))
        self.radio_convert_cbz.setText(QCoreApplication.translate("Widget", "CBZ", None))
        self.label_progress.setText(QCoreApplication.translate("Widget", "Downloading...", None))
        self.button_start.setText(QCoreApplication.translate("Widget", "Start!", None))

    # retranslateUi
