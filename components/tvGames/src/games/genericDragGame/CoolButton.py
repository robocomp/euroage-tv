# -*- coding: utf-8 -*-
"""The user interface for our app"""

import sys
import random
from PySide2 import QtCore
from PySide2.QtCore import QRect
from PySide2.QtGui import QRegion
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect


class CoolButton(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.hello = ["Hallo Welt", "你好，世界", "Hei maailma",
                      "Hola Mundo", "Привет мир"]

        self.button = QPushButton("Click me, Im green!")
        self.button.setFixedWidth(200)
        self.button.setFixedHeight(200)
        self.button.setStyleSheet(" background-color:#74ad5a;;")

        self.button.setMask(QRegion(QRect(5,5,180,180), QRegion.Ellipse))

        self.button2 = QPushButton("Click me, Im red!")
        self.button2.setFixedWidth(200)
        self.button2.setFixedHeight(200)
        self.button2.setStyleSheet(" background-color:#d0451b;")
        self.button2.setMask(QRegion(QRect(5,5,180,180), QRegion.Ellipse))

        self.text = QLabel("Hello World")
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button2)
        self.setLayout(self.layout)

        self.button.pressed.connect(self.magic)
        self.button.released.connect(self.magic2)
        self.button2.clicked.connect(self.magic)

        # TODO: Shadow
        self.buttonShadow = QGraphicsDropShadowEffect(self)
        self.buttonShadow.setBlurRadius(22)
        self.buttonShadow.setOffset(10)
        self.button.setGraphicsEffect(self.buttonShadow)


    def magic(self):
        current_button = self.sender()
        self.buttonShadow = QGraphicsDropShadowEffect(self)
        self.buttonShadow.setBlurRadius(10)
        self.buttonShadow.setOffset(2)
        current_button.setGraphicsEffect(self.buttonShadow)
        current_button.update()
        self.text.setText(random.choice(self.hello))

    def magic2(self):
        current_button = self.sender()
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
