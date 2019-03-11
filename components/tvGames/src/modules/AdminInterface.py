# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdminInterface.ui'
#
# Created: Thu Sep 20 18:58:35 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!
import sys

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QMainWindow, QApplication
from ui_AdminInterface import Ui_AdminInterface

class AdminInterface(QMainWindow, Ui_AdminInterface):
    close_main_window = speak = Signal(str)
    def __init__(self):
        super(AdminInterface, self).__init__()
        self.setupUi(self)

    def update_admin_image(self, image):
        self.admin_image.set_opencv_image(image, False)

    def closeEvent(self, event):
        self.close_main_window.emit()
        super(AdminInterface, self).closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interf = AdminInterface()
    interf.show()
    app.exec_()
