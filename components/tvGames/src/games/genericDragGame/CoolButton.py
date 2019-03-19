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

        self.button.clicked.connect(self.magic)
        self.button2.clicked.connect(self.magic)

        # TODO: Shadow
        # self.buttonShadow = QGraphicsDropShadowEffect(self)
        # self.buttonShadow.setBlurRadius(5)
        # self.button.setGraphicsEffect(self.buttonShadow)


    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CoolButton()
    w.show()
    sys.exit(app.exec_())
