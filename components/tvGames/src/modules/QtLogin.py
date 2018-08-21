#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
from pprint import pprint

import passwordmeter
from PyQt4.QtCore import QObject, pyqtSignal, pyqtWrapperType
from PyQt4.QtGui import QWidget, QLabel, QGroupBox, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication
from passlib.hash import pbkdf2_sha256

FILE_PATH = os.path.abspath(__file__)
# DATABASE_PATH = "resources/users_db.sqlite"
USERS_FILE_PATH = "resources/passwords.json"
SHADOWS_FILE_PATH = "resources/shadows.json"
# print FILE_PATH
print os.getcwd()


# SQL_USER_TABLE_CREATION='create table if not exists users ' \
# 						'(id int unsigned not null,' \
# 						'username varchar(100) not null' \
# 						', password binary(60) not null,' \
# 						' primary key(id), unique(username) ' \
# 						');' \
# 						'create table if not exists roles (' \
# 						'id int unsigned not null,' \
# 						'role varchar(100) not null,' \
# 						'primary key(id),' \
# 						'unique(role)' \
# 						');' \
# 						'create table if not exists user_roles (' \
# 						'user_id int unsigned not null,' \
# 						'role_id int unsigned not null,' \
# 						'unique(user_id, role_id)' \
# 						');'


class DDBBStatus:
	connected = 1
	disconneted = 2


class Singleton(pyqtWrapperType, type):
	def __init__(cls, name, bases, dict):
		super(Singleton, cls).__init__(name, bases, dict)
		cls.instance = None

	def __call__(cls, *args, **kw):
		if cls.instance is None:
			cls.instance = super(Singleton, cls).__call__(*args, **kw)
		return cls.instance


class QUserManager(QObject):
	__metaclass__ = Singleton

	status_changed = pyqtSignal(str)

	def __init__(self, parent=None, **kwargs):
		super(QUserManager, self).__init__(parent, **kwargs)
		# self.users_db = QSqlDatabase.addDatabase("QSQLITE")
		# self.users_db.setDatabaseName(DATABASE_PATH)
		# self.status = DDBBStatus.disconneted
		self.users_data = {}

	# def init_ddbb(self):
	# 	if self.status != DDBBStatus.connected:
	# 		if os.path.isfile(DATABASE_PATH):
	# 			self.open_ddbb()
	# 		else:
	# 			self.status_changed.emit("[!]Creating DDBB file.")
	# 			try:
	# 				conn = sqlite3.connect(DATABASE_PATH)
	# 				print(sqlite3.version)
	# 			except sqlite3.Error as e:
	# 				print(e)
	# 				self.status_changed.emit("[!]DDBB Creation failed")
	# 			finally:
	# 				conn.close()
	# 				self.status_changed.emit("[!]DDBB Created")
	# 				self.open_ddbb()
	# 				query = QSqlQuery(SQL_USER_TABLE_CREATION)
	# 				if not query.exec_():
	# 					print "Creation failed"
	# 				else:
	# 					print "DDBB creation done"
	#
	# 				query.prepare("select * from users")
	# 				if not query.exec_():
	# 					print "Select failed"
	# 				else:
	# 					while query.next():
	# 						print query.value(0).toString()
	# 	else:
	# 		self.status_changed.emit("[+]Connected to DDBB")
	# 		self.status = DDBBStatus.connected

	# def open_ddbb(self):
	# if self.users_db.open():
	# 	self.status_changed.emit("[+]Connected to DDBB")
	# 	self.status = DDBBStatus.connected
	# 	return True
	# else:
	# 	self.status_changed.emit("[!]Fail connecting to DDBB")
	# 	self.status = DDBBStatus.disconneted
	# 	return False

	# open file
	# pass

	def load_users(self):
		with open(USERS_FILE_PATH) as f:
			self.users_data = json.load(f)

		pprint(self.users_data)

	def check_user_password(self, username, password_to_check):
		if len(self.users_data) > 0:
			with open(SHADOWS_FILE_PATH) as f:
				stored_passwords = json.load(f)
				if username in stored_passwords:
					if username in self.users_data:
						if self.users_data[username][2] == '_':
							hash = stored_passwords[username]
							if pbkdf2_sha256.verify(password_to_check, hash):
								return True
							else:
								print "WARNING: check_user_password: password mismatch"
								return False
						else:
							print "ERROR: check_user_password: Password should be shadowed"
					else:
						print "ERROR: check_user_password: username does't exist"
				else:
					print "ERROR: check_user_password: username does't exist"
		else:
			print "ERROR: check_user_password: No user load."
			return False

	def set_username_password(self, username, plain_password, role='admin'):
		with open(SHADOWS_FILE_PATH, "r+") as f:
			stored_passwords = json.load(f)
			stored_passwords[username] = pbkdf2_sha256.hash(plain_password)
			json.dump(stored_passwords, f)
		self.users_data[username] = [username, role, '_']
		with open(USERS_FILE_PATH, "w") as f:
			json.dump(self.users_data, f)



class QLoginWidgetBase(QWidget):
	def __init__(self, parent=None):
		super(QLoginWidgetBase, self).__init__(parent)

		self.user_ddbb_connector = QUserManager()
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
		self.user_ddbb_connector.load_users()

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
	login_executed = pyqtSignal(bool)
	def __init__(self, parent=None):
		super(QLoginWidget, self).__init__(parent)
		self.login_button.clicked.connect(self.check_login)
		self.login_executed.connect(self.update_login_status)

	def check_login(self):
		username = unicode(self.username_lineedit.text())
		password = unicode(self.password_lineedit.text())
		if self.user_ddbb_connector.check_user_password(username, password):
			self.login_executed.emit(True)
		else:
			self.login_executed.emit(False)

	def update_login_status(self, status):
		if not status:
			self.login_status.setText("[!]Login failed")
		else:
			self.login_status.setText("[+]Login OK")


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
		self.password_lineedit.textChanged.connect(self.password_strength_check)
		self.password_2_lineedit.textChanged.connect(self.password_strength_check)
		self.login_button.clicked.connect(self.create_new_user)

	def password_strength_check(self):
		password = unicode(self.password_lineedit.text())
		repeated_password = unicode(self.password_2_lineedit.text())
		strength, improvements = passwordmeter.test(password)

		if strength < 0.5:
			message = ""
			for improve in improvements.values():
				if message != "":
					message += "\n"
				message += u"· " + improve
			self.password_status.setText(message)
			return False
		if repeated_password != password:
			self.password_status.setText(u"Las contraseñas introducidas no coinciden")
			return False
		self.password_status.setText(u"")
		return True

	def check_username(self):
		# user is not empty
		# user doen't exist
		pass

	def check_all(self):
		# check username
		# check password
		pass

	def create_new_user(self):
		if self.password_strength_check():
			username = unicode(self.username_lineedit.text())
			password = unicode(self.password_lineedit.text())
			self.user_ddbb_connector.set_username_password(username, password)
			return True
		else:
			return False


if __name__ == '__main__':
	app = QApplication(sys.argv)
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	login = QLoginWidget()
	login.show()

	signup = QUserManagementWidget()
	signup.show()
	app.exec_()
