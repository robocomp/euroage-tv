# -*- coding: utf-8 -*-
"""The user interface for our app"""

import sys
# from builtins import super, tuple

from PySide2.QtCore import QRect, Qt, QSize, QPoint
from PySide2.QtGui import QRegion, QColor, QIcon, QPixmap, QPainter, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, \
    QHBoxLayout

class CoolButton(QPushButton):
    def __init__(self,image_path, text="", size=200, offset=20, color=QColor("green"), img=None, parent=None):
        super(CoolButton, self).__init__(parent)
        self._size = size
        self._offset = offset
        self.setFixedSize(QSize(size, size))
        self.set_color(color)

        pixmap = QPixmap(image_path).scaled(QSize(size, size))
        painter = QPainter(pixmap)
        f = QFont("Arial",size/12, QFont.Bold)
        painter.setFont(f)
        font_size = QFontMetrics(f).width(text.upper())
        painter.drawText(QPoint((size-font_size)/2+2, size*0.8), text.upper())
        painter.end()
        icon = QIcon(pixmap)

        self.setIcon(icon)
        self.setIconSize(pixmap.rect().size())

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
                "QPushButton:!hover { background-color:" + color.name() + ";  }")
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
    button = CoolButton(text="AYUDA", image_path="/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/button/justQuestion.png")
    button.set_color(QColor("Orange"))
    button2 = CoolButton(text="FINALIZAR", image_path="/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/button/checked.png")
    layout_h = QHBoxLayout()
    layout_h.addWidget(button)
    layout_h.addWidget(button2)

    layout_v = QVBoxLayout()
    layout_v.addWidget(text)
    layout_v.addLayout(layout_h)
    widget.setLayout(layout_v)
    widget.show()
    sys.exit(app.exec_())
