# -*- coding: utf-8 -*-
"""The user interface for our app"""

import sys
import random
from copy import copy

from PySide2.QtCore import QRect, Qt, QSize
from PySide2.QtGui import QRegion
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect



class CoolButton(QPushButton):
    def __init__(self, text="", size =200, offset = 20, parent=None):
        super(CoolButton, self).__init__(text, parent)
        self._size = size
        self._offset = offset
        self.setFixedSize(QSize(size, size))

        self.setStyleSheet(
            "QPushButton:hover {background-color: green; border: none;} QPushButton:!hover { background-color:#74ad5a;  }")
        # self.setMask(QRegion(QRect(OFFSET/4, OFFSET/4, self._size-OFFSET, self._size-OFFSET), QRegion.Ellipse))
        self.setMask(
            QRegion(QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2, self._size - self._offset, self._size - self._offset),
                    QRegion.Ellipse))

        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

        # Shadow
        self._set_released_shadow()



    def _set_pressed_shadow(self):
        pressed_shadow = QGraphicsDropShadowEffect(self)
        pressed_shadow.setBlurRadius(10)
        pressed_shadow.setOffset(2)
        self.setGraphicsEffect(pressed_shadow)
        self.update()

    def _set_released_shadow(self):
        released_shadow = QGraphicsDropShadowEffect(self)
        released_shadow.setBlurRadius(22)
        released_shadow.setOffset(10)
        self.setGraphicsEffect(released_shadow)
        self.update()


    def _button_pressed(self):
        current_button = self.sender()
        current_button.w, current_button.h = current_button.width() - self._offset, current_button.height() - self._offset
        current_button.offset = self._offset / 2

        current_button.setMask(QRegion(QRect(
            (self._size - (current_button.w + current_button.offset)) / 2,
            (self._size - (current_button.h + current_button.offset)) / 2,
            current_button.w + current_button.offset,
            current_button.h + current_button.offset), QRegion.Ellipse))


        self._set_pressed_shadow()

    def _button_released(self):
        current_button = self.sender()
        current_button.setMask(
            QRegion(QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2, self._size - self._offset, self._size - self._offset),
                    QRegion.Ellipse))

        self._set_released_shadow()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QWidget()
    text = QLabel()
    text = QLabel("Hello World")
    text.setAlignment(Qt.AlignCenter)
    button = CoolButton()
    button2 = CoolButton()
    layout = QVBoxLayout()
    layout.addWidget(text)
    layout.addWidget(button)
    layout.addWidget(button2)
    widget.setLayout(layout)
    widget.show()
    sys.exit(app.exec_())
