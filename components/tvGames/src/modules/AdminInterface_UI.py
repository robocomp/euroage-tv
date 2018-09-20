# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdminInterface.ui'
#
# Created: Thu Sep 20 19:22:54 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AdminInterface(object):
    def setupUi(self, AdminInterface):
        AdminInterface.setObjectName("AdminInterface")
        AdminInterface.resize(800, 600)
        self.centralwidget = QtGui.QWidget(AdminInterface)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.admin_image = QImageWidget(self.centralwidget)
        self.admin_image.setObjectName("admin_image")
        self.verticalLayout.addWidget(self.admin_image)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.remove_player_button = QtGui.QPushButton(self.centralwidget)
        self.remove_player_button.setEnabled(False)
        self.remove_player_button.setObjectName("remove_player_button")
        self.horizontalLayout.addWidget(self.remove_player_button)
        self.add_player_button = QtGui.QPushButton(self.centralwidget)
        self.add_player_button.setObjectName("add_player_button")
        self.horizontalLayout.addWidget(self.add_player_button)
        self.players_lcd = QtGui.QLCDNumber(self.centralwidget)
        self.players_lcd.setObjectName("players_lcd")
        self.horizontalLayout.addWidget(self.players_lcd)
        self.verticalLayout.addLayout(self.horizontalLayout)
        AdminInterface.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(AdminInterface)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        AdminInterface.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(AdminInterface)
        self.statusbar.setObjectName("statusbar")
        AdminInterface.setStatusBar(self.statusbar)

        self.retranslateUi(AdminInterface)
        QtCore.QMetaObject.connectSlotsByName(AdminInterface)

    def retranslateUi(self, AdminInterface):
        AdminInterface.setWindowTitle(QtGui.QApplication.translate("AdminInterface", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_player_button.setText(QtGui.QApplication.translate("AdminInterface", "Remove player", None, QtGui.QApplication.UnicodeUTF8))
        self.add_player_button.setText(QtGui.QApplication.translate("AdminInterface", "Add player", None, QtGui.QApplication.UnicodeUTF8))

from modules.QImageWidget import QImageWidget
