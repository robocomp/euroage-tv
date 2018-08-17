#!/usr/bin/env python
# -*- coding: utf-8 -*-


import signal
import sqlite3
import sys
import os

from PyQt4.QtGui import QWidget, QLabel, QGroupBox, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication
from PyQt4.QtSql import QSqlDatabase

FILE_PATH = os.path.abspath(__file__)
DATABASE_PATH = "resources/users_db.sqlite"
print FILE_PATH
print os.getcwd()

class QLogin(QWidget):
	def __init__(self, parent = None):
		super(QLogin, self).__init__(parent)

		users_db = QSqlDatabase.addDatabase("QSQLITE")
		users_db.setDatabaseName(DATABASE_PATH)


		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.username_layout = QHBoxLayout()
		self.username_label = QLabel(u"Usuario:")
		self.username_lineedit = QLineEdit()
		self.password_layout = QHBoxLayout()
		self.password_label = QLabel(u"Contraseña:")
		self.password_lineedit = QLineEdit()
		self.password_lineedit.setEchoMode(QLineEdit.Password)
		self.login_button_layout = QHBoxLayout()
		self.login_button = QPushButton(u"Iniciar sesión")
		self.login_status = QLabel("[+]")
		f = self.login_status.font()
		f.setPointSize(8)  # sets the size to 27
		self.login_status.setFont(f)

		self.login_groupbox = QGroupBox()
		self.login_layout = QVBoxLayout()

		self.username_layout.addWidget(self.username_label)
		self.username_layout.addStretch()
		self.username_layout.addWidget(self.username_lineedit)

		self.password_layout.addWidget(self.password_label)
		self.password_layout.addStretch()
		self.password_layout.addWidget(self.password_lineedit)

		self.login_button_layout.addWidget(self.login_status)
		self.login_button_layout.addStretch()
		self.login_button_layout.addWidget(self.login_button)


		self.login_layout.addLayout(self.username_layout)
		self.login_layout.addLayout(self.password_layout)
		self.login_layout.addLayout(self.login_button_layout)

		self.login_groupbox.setLayout(self.login_layout)
		self.main_layout.addWidget(self.login_groupbox)


		if os.path.isfile(DATABASE_PATH):
			if users_db.open():
				self.login_status.setText("[+]Connected to DDBB")
			else:
				self.login_status.setText("[!]Fail connecting to DDBB")
		else:
			try:
				conn = sqlite3.connect(DATABASE_PATH)
				print(sqlite3.version)
			except sqlite3.Error as e:
				print(e)
				self.login_status.setText("[!]DDBB file doesn't exists")
			finally:
				conn.close()




if __name__ == '__main__':
	app = QApplication(sys.argv)
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	login = QLogin()
	login.show()
	app.exec_()




