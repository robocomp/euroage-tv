# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdminInterface.ui'
#
# Created: Thu Sep 20 18:58:35 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!
import sys

from PySide2.QtCore import Signal, QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from ui_AdminInterface import Ui_AdminInterface

## Comprobar si así va bien
class AdminInterface(QWidget): # crea widget vacio
    def __init__(self,parent = None):
        super(AdminInterface, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(AdminInterface)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/AdminInterface_new.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()

    def update_admin_image(self, image):
        self.ui.admin_image.set_opencv_image(image, False)

    def closeEvent(self, event):
        self.close_main_window.emit()
        super(AdminInterface, self).closeEvent(event)

# class AdminInterface(QMainWindow, Ui_AdminInterface):
#     close_main_window = speak = Signal(str)
#     def __init__(self):
#         super(AdminInterface, self).__init__()
#         self.setupUi(self)
#
#     def update_admin_image(self, image):
#         self.admin_image.set_opencv_image(image, False)
#
#     def closeEvent(self, event):
#         self.close_main_window.emit()
#         super(AdminInterface, self).closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # interf = AdminInterface()
    interf = AdminInterface()
    interf.show()
    app.exec_()
