# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdminInterface.ui'
#
# Created: Thu Sep 20 18:58:35 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!
import sys

from PySide.QtGui import QMainWindow, QApplication
from AdminInterface_UI import Ui_AdminInterface

class AdminInterface(QMainWindow, Ui_AdminInterface):
    def __init__(self):
        super(AdminInterface, self).__init__()
        self.setupUi(self)

    def update_admin_image(self, image):
        self.admin_image.set_opencv_image(image, False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interf = AdminInterface()
    interf.show()
    app.exec_()
