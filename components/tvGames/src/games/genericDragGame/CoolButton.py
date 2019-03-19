# -*- coding: utf-8 -*-
"""The user interface for our app"""

import sys
import random
from copy import copy

from PySide2.QtCore import QRect, Qt
from PySide2.QtGui import QRegion
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect

SIZE = 200
OFFSET = 20


class CoolButton(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.hello = ["Hallo Welt", "你好，世界", "Hei maailma",
                      "Hola Mundo", "Привет мир"]

        self.button = QPushButton("Click me, Im greeeeeeeen!")
        self.button.setFixedWidth(SIZE)
        self.button.setFixedHeight(SIZE)
        self.button.setStyleSheet(
            "QPushButton:hover {background-color: green; border: none;} QPushButton:!hover { background-color:#74ad5a;  }")
        # self.button.setMask(QRegion(QRect(OFFSET/4, OFFSET/4, SIZE-OFFSET, SIZE-OFFSET), QRegion.Ellipse))
        self.button.setMask(
            QRegion(QRect((SIZE - (SIZE - OFFSET)) / 2, (SIZE - (SIZE - OFFSET)) / 2, SIZE - OFFSET, SIZE - OFFSET),
                    QRegion.Ellipse))

        self.button2 = QPushButton("Click me, Im reeeeeed!")
        self.button2.setFixedWidth(SIZE)
        self.button2.setFixedHeight(SIZE)

        self.button2.setStyleSheet(
            "QPushButton:hover {background-color: red; border: none;} QPushButton:!hover { background-color:#d0451b;  }")

        self.button2.setMask(
            QRegion(QRect((SIZE - (SIZE - OFFSET)) / 2, (SIZE - (SIZE - OFFSET)) / 2, SIZE - OFFSET, SIZE - OFFSET),
                    QRegion.Ellipse))

        self.text = QLabel("Hello World")

        self.text.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)
        self.setLayout(self.layout)

        self.button.pressed.connect(self.magic)
        self.button.released.connect(self.magic2)
        self.button2.pressed.connect(self.magic)
        self.button2.released.connect(self.magic2)

        # Shadow
        self.buttonShadow = QGraphicsDropShadowEffect(self)
        self.buttonShadow.setBlurRadius(22)
        self.buttonShadow.setOffset(10)
        self.buttonShadow2 = QGraphicsDropShadowEffect(self)
        self.buttonShadow2.setBlurRadius(22)
        self.buttonShadow2.setOffset(10)
        self.button.setGraphicsEffect(self.buttonShadow)
        self.button2.setGraphicsEffect(self.buttonShadow2)

    def magic(self):
        current_button = self.sender()
        current_button.w, current_button.h = current_button.width() - OFFSET, current_button.height() - OFFSET
        current_button.offset = OFFSET / 2

        current_button.setMask(QRegion(QRect(
            (SIZE - (current_button.w + current_button.offset)) / 2,
            (SIZE - (current_button.h + current_button.offset)) / 2,
            current_button.w + current_button.offset,
            current_button.h + current_button.offset), QRegion.Ellipse))

        self.buttonShadow = QGraphicsDropShadowEffect(self)
        self.buttonShadow.setBlurRadius(10)
        self.buttonShadow.setOffset(2)

        current_button.setGraphicsEffect(self.buttonShadow)
        current_button.update()
        self.text.setText(random.choice(self.hello))

    def magic2(self):
        current_button = self.sender()
        current_button.setMask(
            QRegion(QRect((SIZE - (SIZE - OFFSET)) / 2, (SIZE - (SIZE - OFFSET)) / 2, SIZE - OFFSET, SIZE - OFFSET),
                    QRegion.Ellipse))
        self.buttonShadow = QGraphicsDropShadowEffect(self)
        self.buttonShadow.setBlurRadius(22)
        self.buttonShadow.setOffset(10)
        current_button.setGraphicsEffect(self.buttonShadow)
        current_button.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CoolButton()
    w.show()
    sys.exit(app.exec_())
