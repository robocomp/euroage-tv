#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
from passlib.hash import pbkdf2_sha256
from pprint import pprint

import passwordmeter
from PySide2.QtCore import QObject, Signal, QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox

from admin_widgets import LoginWindow, RegisterWindow

FILE_PATH = os.path.abspath(__file__)
print(FILE_PATH)
# DATABASE_PATH = "resources/users_db.sqlite"
USERS_FILE_PATH = "../../resources/passwords.json"
SHADOWS_FILE_PATH = "../../resources/shadows.json"
# print FILE_PATH
#print os.getcwd()


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


class Singleton(type(QObject), type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class QUserManager(QObject):
    __metaclass__ = Singleton

    status_changed = Signal(str)

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
            print ("[INFO] Loading users ...")
            self.users_data = json.load(f)

        pprint(self.users_data)

    def check_user_password(self, username, password_to_check):
        print ("[INFO] Checking password ...")
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
                                print ("WARNING: check_user_password: password mismatch")
                                return False
                        else:
                            print ("ERROR: check_user_password: Password should be shadowed")
                    else:
                        print ("ERROR: check_user_password: username does't exist")
                else:
                    print ("ERROR: check_user_password: username does't exist")
        else:
            print ("ERROR: check_user_password: No user load.")
            return False

    def set_username_password(self, username, plain_password, role='admin'):
        with open(SHADOWS_FILE_PATH, "r") as f:
            stored_passwords = json.load(f)
        with open(SHADOWS_FILE_PATH, "w") as f:
            stored_passwords[username] = pbkdf2_sha256.hash(plain_password)
            json.dump(stored_passwords, f)
        self.users_data[username] = [username, role, '_']
        with open(USERS_FILE_PATH, "w") as f:
            json.dump(self.users_data, f)

    def check_user(self,username): #Return true when the user is found
        if len(self.users_data) > 0:
            if username in self.users_data:
                return True
            else:
                return False
        else:
            return False



class MainWindow(QWidget):
    login_executed = Signal(bool)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #User Management
        self.user_ddbb_connector = QUserManager()
        self.user_ddbb_connector.status_changed.connect(self.ddbb_status_changed)
        self.user_ddbb_connector.load_users()


        #Load widget from ui
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(LoginWindow)
        loader.registerCustomWidget(RegisterWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/modules/mainUI.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        self.ui.stackedWidget.setCurrentIndex(0)
        
        file.close()

        ## Login window
        self.ui.login_button_2.clicked.connect(self.check_login)
        self.ui.newuser_button_2.clicked.connect(self.newuser_clicked)
        self.login_executed.connect(self.update_login_status)

        ## Register window
        self.ui.password_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.password_2_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.createuser_button_reg.clicked.connect(self.create_new_user)
        self.ui.back_button_reg.clicked.connect(self.back_clicked)


    def ddbb_status_changed(self, string):
        self.ui.login_status.setText(string)

    #Login window functions
    def check_login(self):
        print ("[INFO] Checking login ...")

        username = unicode(self.ui.username_lineedit.text())
        password = unicode(self.ui.password_lineedit.text())

        if self.user_ddbb_connector.check_user_password(username, password):
            print("Yess")
            self.login_executed.emit(True)
        else:
            QMessageBox().information(self.focusWidget(), 'Error',
                                      'Username or password incorrect',
                                      QMessageBox.Ok)
            self.login_executed.emit(False)

    def update_login_status(self, status):
        if not status:
            self.ui.login_status.setText("[!]Login failed")
        else:
            self.ui.login_status.setText("[+]Login OK")

    def newuser_clicked(self):
        index = self.ui.stackedWidget.indexOf(self.ui.register_page)
        self.ui.stackedWidget.setCurrentIndex(index)


    #Register window functions
    def password_strength_check(self):
        password = unicode(self.ui.password_lineedit_reg.text())
        repeated_password = unicode(self.ui.password_2_lineedit_reg.text())
        strength, improvements = passwordmeter.test(password)

        if strength < 0.5:
            message = ""
            for improve in improvements.values():
                if message != "":
                    message += "\n"
                message += u"· " + improve
            self.ui.password_status_reg.setText(message)
            return False
        if repeated_password != password:
            self.ui.password_status_reg.setText(u"Las contraseñas introducidas no coinciden")
            return False
        self.ui.password_status_reg.setText(u"")
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
        print ("[INFO] Trying to create new user ...")

        if self.password_strength_check():
            username = unicode(self.ui.username_lineedit_reg.text())
            password = unicode(self.ui.password_lineedit_reg.text())

            if (self.user_ddbb_connector.check_user(username) == True): #The user already exist
                QMessageBox().information(self.focusWidget(), 'Error',
                                          'The username already exist',
                                          QMessageBox.Ok)
                return False
            else:
                self.user_ddbb_connector.set_username_password(username, password)
                print ("[INFO] User created correctly")
                return True
        else:
            print ("[ERROR] The user couldn't be created ")
            return False

    def back_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(0)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    main = MainWindow()
    main.show()


    app.exec_()
