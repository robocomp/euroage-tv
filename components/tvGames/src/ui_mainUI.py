# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mainUI.ui'
#
# Created: Thu Aug 30 13:50:05 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!
from PySide2.QtCore import QMetaObject, QCoreApplication
from PySide2.QtWidgets import QApplication


class Ui_guiDlg(object):
    def setupUi(self, guiDlg):
        guiDlg.setObjectName("guiDlg")
        guiDlg.resize(400, 300)

        self.retranslateUi(guiDlg)
        QMetaObject.connectSlotsByName(guiDlg)

    def retranslateUi(self, guiDlg):
        guiDlg.setWindowTitle(QApplication.translate("guiDlg", "tvgames", None))

