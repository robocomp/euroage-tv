# -*- coding: utf-8 -*-
"""The user interface for our app"""

import sys
import random
from copy import copy

from PySide2.QtCore import QRect, Qt, QSize
from PySide2.QtGui import QRegion, QColor
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, \
    QHBoxLayout


class CoolButton(QPushButton):
    def __init__(self, text="", size=200, offset=20, color=QColor("green"), parent=None):
        super(CoolButton, self).__init__(text, parent)
        self._size = size
        self._offset = offset
        self.setFixedSize(QSize(size, size))
        self.set_color(color)

        # self.setMask(QRegion(QRect(OFFSET/4, OFFSET/4, self._size-OFFSET, self._size-OFFSET), QRegion.Ellipse))
        self.setMask(
            QRegion(
                QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2,
                      self._size - self._offset, self._size - self._offset),
                QRegion.Ellipse))

        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

        # Shadow
        self._set_released_shadow()

    def set_color(self, color):
        if isinstance(color, QColor):
            self.setStyleSheet(
                "QPushButton:hover {background-color: " + color.darker().name() + "; border: none;} QPushButton:!hover { background-color:" + color.name() + ";  }")
            self.update()
        else:
            raise Exception("color must be a QColor class")

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
        self.w, self.h = self.width() - self._offset, self.height() - self._offset
        self.offset = self._offset / 2

        self.setMask(QRegion(QRect(
            (self._size - (self.w + self.offset)) / 2,
            (self._size - (self.h + self.offset)) / 2,
            self.w + self.offset,
            self.h + self.offset), QRegion.Ellipse))

        self._set_pressed_shadow()

    def _button_released(self):
        self.setMask(
            QRegion(
                QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2,
                      self._size - self._offset, self._size - self._offset),
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
    layout_h = QHBoxLayout()
    layout_h.addWidget(button)
    layout_h.addWidget(button2)

    layout_v = QVBoxLayout()
    layout_v.addWidget(text)
    layout_v.addLayout(layout_h)
    widget.setLayout(layout_v)
    widget.show()
    sys.exit(app.exec_())
