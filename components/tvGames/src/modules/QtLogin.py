#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import signal
import sqlite3
import sys
import os

import passwordmeter
from PyQt4.QtCore import QObject, pyqtSignal, pyqtWrapperType
from PyQt4.QtGui import QWidget, QLabel, QGroupBox, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication
from PyQt4.QtSql import QSqlDatabase

FILE_PATH = os.path.abspath(__file__)
DATABASE_PATH = "resources/users_db.sqlite"
print FILE_PATH
print os.getcwd()

class DDBBStatus:
	connected = 1
	disconneted = 2

class Singleton(pyqtWrapperType, type):
	def __init__(cls, name, bases, dict):
		super(Singleton, cls).__init__(name, bases, dict)
		cls.instance=None

	def __call__(cls,*args,**kw):
		if cls.instance is None:
			cls.instance=super(Singleton, cls).__call__(*args, **kw)
		return cls.instance



class QUserDDBBManager(QObject):
	__metaclass__ = Singleton

	status_changed = pyqtSignal(str)

	def __init__(self, parent=None, **kwargs):
		super(QUserDDBBManager, self).__init__(parent, **kwargs)
		self.users_db = QSqlDatabase.addDatabase("QSQLITE")
		self.users_db.setDatabaseName(DATABASE_PATH)
		self.status = DDBBStatus.disconneted

	def init_ddbb(self):
		if self.status != DDBBStatus.connected:
			if os.path.isfile(DATABASE_PATH):
				self.open_ddbb()
			else:
				self.status_changed.emit("[!]Creating DDBB file.")
				try:
					conn = sqlite3.connect(DATABASE_PATH)
					print(sqlite3.version)
				except sqlite3.Error as e:
					print(e)
					self.status_changed.emit("[!]DDBB Creation failed")
				finally:
					conn.close()
					self.status_changed.emit("[!]DDBB Created")
					self.open_ddbb()
					query = QSqlQuery("CREATE TABLE users (userId INTEGER, PRIMARY K)")
					if (!query.exec ())
						pass

					query.prepare("INSERT INTO tasks (taskId) VALUES (:id)")
					query.bindValue(":id", valueForInitialization)
					if (!query.exec ())
						pass
		else:
			self.status_changed.emit("[+]Connected to DDBB")
			self.status = DDBBStatus.connected

	def open_ddbb(self):
		if self.users_db.open():
			self.status_changed.emit("[+]Connected to DDBB")
			self.status = DDBBStatus.connected
			return True
		else:
			self.status_changed.emit("[!]Fail connecting to DDBB")
			self.status = DDBBStatus.disconneted
			return False


class QLoginWidgetBase(QWidget):
	def __init__(self, parent = None):
		super(QLoginWidgetBase, self).__init__(parent)

		self.user_ddbb_connector = QUserDDBBManager()
		self.user_ddbb_connector.status_changed.connect(self.ddbb_status_changed)

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
		f.setPointSize(6)
		self.login_status.setFont(f)

		self.login_groupbox = QGroupBox(u"Iniciar sesión::")
		self.login_layout = QVBoxLayout()

		self.build_widget()
		self.user_ddbb_connector.init_ddbb()

	def build_widget(self):
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


	def ddbb_status_changed(self, string):
		self.login_status.setText(string)

class QLoginWidget(QLoginWidgetBase):
	def __init__(self, parent=None):
		super(QLoginWidget, self).__init__(parent)


class QUserManagementWidget(QLoginWidgetBase):
	def __init__(self, parent=None):
		self.password_2_layout = QHBoxLayout()
		self.password_2_label = QLabel(u"Repetir contraseña:")
		self.password_2_lineedit = QLineEdit()
		self.password_2_lineedit.setEchoMode(QLineEdit.Password)
		self.password_status = QLabel("")
		f = self.password_status.font()
		f.setPointSize(6)
		self.password_status.setFont(f)
		super(QUserManagementWidget, self).__init__(parent)
		self.login_button.setText(u"Crear usuario")
		self.login_groupbox.setTitle(u"Nuevo usuario:")


	def build_widget(self):
		self.username_layout.addWidget(self.username_label)
		self.username_layout.addStretch()
		self.username_layout.addWidget(self.username_lineedit)

		self.password_layout.addWidget(self.password_label)
		self.password_layout.addStretch()
		self.password_layout.addWidget(self.password_lineedit)

		self.password_2_layout.addWidget(self.password_2_label)
		self.password_2_layout.addStretch()
		self.password_2_layout.addWidget(self.password_2_lineedit)

		self.login_button_layout.addWidget(self.login_status)
		self.login_button_layout.addStretch()
		self.login_button_layout.addWidget(self.login_button)

		self.login_layout.addLayout(self.username_layout)
		self.login_layout.addLayout(self.password_layout)
		self.login_layout.addLayout(self.password_2_layout)
		self.login_layout.addWidget(self.password_status)
		self.login_layout.addLayout(self.login_button_layout)

		self.login_groupbox.setLayout(self.login_layout)
		self.main_layout.addWidget(self.login_groupbox)
		self.user_ddbb_connector.init_ddbb()
		self.password_lineedit.textChanged.connect(self.password_check)
		self.password_2_lineedit.textChanged.connect(self.password_check)
		self.login_button.clicked.connect(self.create_new_user)

	def password_check(self):
		password = unicode(self.password_lineedit.text())
		repeated_password = unicode(self.password_2_lineedit.text())
		strength, improvements = passwordmeter.test(password)

		if strength < 0.5:
			message = ""
			for improve in improvements.values():
				if message!="":
					message +="\n"
				message += u"· "+improve
			self.password_status.setText(message)
			return False
		if repeated_password != password:
			self.password_status.setText(u"Las contraseñas introducudas no coinciden")
			return False
		self.password_status.setText(u"")

	def check_username(self):
		# user is not empty
		# user doen't exist
		pass


	def check_all(self):
		#check username
		#check password
		pass

	def create_new_user(self):






if __name__ == '__main__':
	app = QApplication(sys.argv)
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	login = QLoginWidget()
	login.show()

	signup = QUserManagementWidget()
	signup.show()
	app.exec_()




