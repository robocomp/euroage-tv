#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2019 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import datetime

from genericworker import *
import json
import os
import signal
import sys
from passlib.hash import pbkdf2_sha256
from pprint import pprint

import passwordmeter
from PySide2.QtCore import QObject, Signal, QFile, QModelIndex
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMessageBox, QCompleter, QMainWindow, QAction, qApp
import csv

from admin_widgets import *

try:
    from bbdd import BBDD
except:
    print ("Database module not found")

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

FILE_PATH = os.path.abspath(__file__)
CURRENT_PATH = os.path.dirname(__file__)

print(FILE_PATH)
# DATABASE_PATH = "resources/users_db.sqlite"
USERS_FILE_PATH = "src/passwords.json"
SHADOWS_FILE_PATH = "src/shadows.json"
# print FILE_PATH
# print os.getcwd()

list_of_users = []
list_of_games = ["Juego 1", "Juego 2", "Juego 3", "Juego 4"]


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


class Session():
    def __init__(self):
        self.date = None
        self.patient = None
        self.totaltime = 0
        self.games = []
        self.numGames = 0
        self.totalHelps = 0
        self.totalChecks = 0
        self.wonGames = 0
        self.lostGames = 0

    def save_session(self):
        saving_dir = os.path.join(CURRENT_PATH, "../savedSessions")
        patient = self.patient.replace(" ", "").strip()
        patient_dir = os.path.join(saving_dir, patient)

        if not os.path.isdir(patient_dir):
            os.mkdir(patient_dir)

        date = datetime.strftime(self.date, "%y%m%d_%H%M%S")
        date_dir = os.path.join(patient_dir, date)

        if os.path.isdir(date_dir):
            print ("Error, la sesion ya ha sido guardada")
            return
        else:
            os.mkdir(date_dir)

            for game in self.games:
                game.save_game(date_dir)

            rows = [['tiempo total',  'num juegos', 'num ayudas', 'num comprobaciones',  'juegos ganados', 'juegos perdidos'],
                    [self.totaltime, len(self.games),  self.totalHelps, self.totalChecks, self.wonGames, self.lostGames ]]

            filename = os.path.join(date_dir, "resumeSession"+ ".csv")

            with open(filename, 'w') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerows(rows)
            csvFile.close()


class Game():
    def __init__(self):
        self.nameGame = None
        self.date = None
        self.timePlayed = 0
        self.timePaused = 0
        self.distance = 0
        self.touched = 0
        self.handClosed = 0
        self.helps = 0
        self.checks = 0
        self.hits = 0
        self.fails = 0
        self.gameWon = False

    def save_game(self, dir):
        name = self.nameGame
        filename = os.path.join(dir, name.replace(" ", "").strip().lower() + ".csv")
        date = datetime.strftime(self.date, "%H:%M:%S")

        rows = [['hora comienzo', 'tiempo total', 'tiempo pausado', 'distancia recorrida', 'num pantalla pulsada',
                 'num mano cerrada', 'num ayudas', 'num comprobaciones', 'aciertos', 'fallos', 'juego ganado'],
                [date, self.timePlayed, self.timePaused, self.distance, self.touched, self.handClosed, self.helps,
                 self.checks, self.hits, self.fails, self.gameWon]
                ]

        with open(filename, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(rows)
        csvFile.close()


class QUserManager(QObject):
    __metaclass__ = Singleton

    status_changed = Signal(str)

    def __init__(self, parent=None, **kwargs):
        super(QUserManager, self).__init__(parent, **kwargs)
        # self.users_db = QSqlDatabase.addDatabase("QSQLITE")
        # self.users_db.setDatabaseName(DATABASE_PATH)
        # self.status = DDBBStatus.disconneted
        self.users_data = {}

    def load_users(self):
        with open(USERS_FILE_PATH) as f:
            print ("[INFO] Loading users ...")
            self.users_data = json.load(f)
            for user, algo in self.users_data.items():
                list_of_users.append(user)
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

    def check_user(self, username):  # Return true when the user is found
        if len(self.users_data) > 0:
            if username in self.users_data:
                return True
            else:
                return False
        else:
            return False


class SpecificWorker(GenericWorker):
    login_executed = Signal(bool)
    endGameSig = Signal(bool, str)
    resetGameSig = Signal()
    playGameSig = Signal(str)
    endSessionSig = Signal(str)
    initGameSig = Signal()
    pausedGameSig = Signal(str)

    updateUISig = Signal(bool)

    def __init__(self, proxy_map):

        super(SpecificWorker, self).__init__(proxy_map)
        self.timer.timeout.connect(self.compute)
        self.Period = 2000

        self.user_ddbb_connector = QUserManager()
        self.user_ddbb_connector.status_changed.connect(self.ddbb_status_changed)
        self.user_ddbb_connector.load_users()

        self.init_ui()
        self.setCentralWidget(self.ui)

        self.sessions = []
        self.currentSession = Session()
        self.currentGame = Game()

        self.aux_datePaused = None
        self.aux_currentDate = None
        self.aux_currentStatus = None

        self.endGameSig.connect(self.state_end_game)
        self.playGameSig.connect(self.state_playing)
        self.resetGameSig.connect(self.state_reset_game)
        self.endSessionSig.connect(self.state_finish_session)
        self.initGameSig.connect(self.state_ready)
        self.pausedGameSig.connect(self.state_paused)

        self.updateUISig.connect(self.updateUI)

        self.timer.start(self.Period)

    def init_ui(self):
        loader = QUiLoader()
        loader.registerCustomWidget(LoginWindow)
        loader.registerCustomWidget(RegisterWindow)
        loader.registerCustomWidget(UsersWindow)
        loader.registerCustomWidget(PlayersWindow)
        loader.registerCustomWidget(GameWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/stackedUI.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        file.close()

        self.ui.stackedWidget.setCurrentIndex(2)  # Poner a 0

        ##Menu
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu('&Menú')
        if (self.ui.stackedWidget.currentIndex == 0 or self.ui.stackedWidget.currentIndex == 1):
            self.mainMenu.setEnabled(False)

        exitAction = QAction('&Salir', self)
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        closeAction = QAction('&Cerrar sesión', self)
        closeAction.triggered.connect(self.close_thsession_clicked)
        fileMenu.addAction(closeAction)

        ## Login window
        self.ui.login_button_2.clicked.connect(self.check_login)
        self.ui.newuser_button_2.clicked.connect(self.newuser_clicked)
        self.login_executed.connect(self.update_login_status)

        completer = QCompleter(list_of_users)
        self.ui.username_lineedit.setCompleter(completer)

        ## Register window
        self.ui.password_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.password_2_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.createuser_button_reg.clicked.connect(self.create_new_user)
        self.ui.back_button_reg.clicked.connect(self.goto_prevScreen)

        ##Users window
        self.bbdd = BBDD()
        self.bbdd.open_database("/home/robocomp/robocomp/components/euroage-tv/components/bbdd/prueba.db")
        patients = self.bbdd.get_all_patients()
        list = []
        for p in patients:
            list.append(p.name + " " + p.surname)

        completer2 = QCompleter(list)
        self.ui.selplayer_combobox.addItems(list)
        self.ui.selplayer_combobox.setCompleter(completer2)
        self.ui.selplayer_combobox.lineEdit().setPlaceholderText("Selecciona jugador...")
        self.selected_player_incombo = ""
        self.ui.selgame_combobox.lineEdit().setPlaceholderText("Selecciona juego...")

        completer3 = QCompleter(list_of_games)
        self.ui.selgame_combobox.addItems(list_of_games)
        self.ui.selgame_combobox.setCompleter(completer3)

        self.selected_game_inlist = ""
        self.selected_game_incombo = ""
        self.list_games_toplay = []
        self.ui.games_list.currentItemChanged.connect(self.selectediteminlist_changed)
        self.ui.selplayer_combobox.currentIndexChanged.connect(self.selectedplayer_changed)
        self.ui.addgame_button.clicked.connect(self.addgametolist)
        self.ui.deletegame_button.clicked.connect(self.deletegamefromlist)
        self.ui.startsession_button.clicked.connect(self.start_session)
        # self.ui.seedata_button.clicked.connect(self.see_userdata)
        self.ui.up_button.clicked.connect(self.movelist_up)
        self.ui.down_button.clicked.connect(self.movelist_down)

        ##new Player window
        self.ui.back_player_button.clicked.connect(self.goto_prevScreen)
        self.ui.create_player_button.clicked.connect(self.create_player)

        # Game window
        self.ui.start_game_button.clicked.connect(self.start_clicked)
        self.ui.pause_game_button.clicked.connect(self.pause_clicked)
        self.ui.continue_game_button.clicked.connect(self.continue_clicked)
        self.ui.finish_game_button.clicked.connect(self.finish_clicked)
        self.ui.reset_game_button.clicked.connect(self.reset_clicked)
        self.ui.end_session_button.clicked.connect(self.end_session_clicked)

        self.ui.start_game_button.setEnabled(False);
        self.ui.pause_game_button.setEnabled(False);
        self.ui.continue_game_button.setEnabled(False);
        self.ui.finish_game_button.setEnabled(False);
        self.ui.reset_game_button.setEnabled(False);

    def start_clicked(self):  # Ver como administrar la lista de juegos
        game = self.list_games_toplay[0]
        self.currentGame = Game()
        self.currentGame.nameGame = game
        self.admingame_proxy.adminStartGame(game)

    def pause_clicked(self):
        self.admingame_proxy.adminPauseGame()

    def continue_clicked(self):
        self.admingame_proxy.adminContinueGame()

    def finish_clicked(self):
        reply = QMessageBox.question(self.focusWidget(), '',
                                     ' Desea finalizar juego?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminStopGame()

    def reset_clicked(self):
        reply = QMessageBox.question(self.focusWidget(), '',
                                     ' Desea volver a empezar? Los datos del juego no se guardarán', QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminResetGame()

    def start_session(self):

        player = self.selected_player_incombo
        self.list_games_toplay = []
        for index in xrange(self.ui.games_list.count()):
            self.list_games_toplay.append(self.ui.games_list.item(index).text())

        if player == "":
            QMessageBox().information(self.focusWidget(), 'Error',
                                      'No se han seleccionado ningún jugador',
                                      QMessageBox.Ok)
        else:
            self.ui.stackedWidget.setCurrentIndex(4)

            self.currentSession.patient = str(player)
            self.admingame_proxy.adminStartSession(player)
            QMessageBox().information(self.focusWidget(), 'Info',
                                      'Coloque la mano del paciente sobre la mesa. Cuando se haya detectado correctamente podrá empezar el juego',
                                      QMessageBox.Ok)

            game = self.list_games_toplay[0]
            self.ui.info_game_label.setText(game)

    def end_session_clicked(self):

        reply = QMessageBox.question(self.focusWidget(), '',
                                     ' ¿Desea finalizar la sesión?', QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminEndSession()

    def setParams(self, params):
        return True

    def ddbb_status_changed(self, string):
        self.ui.login_status.setText(string)

    # Login window functions
    def check_login(self):
        print ("[INFO] Checking login ...")

        username = unicode(self.ui.username_lineedit.text())
        # username = username.strip().lower() ##The username is stored and checked in lower case
        password = unicode(self.ui.password_lineedit.text())

        if self.user_ddbb_connector.check_user_password(username, password):

            self.ui.stackedWidget.setCurrentIndex(2)
            self.mainMenu.setEnabled(True)
            self.login_executed.emit(True)
        else:
            QMessageBox().information(self.focusWidget(), 'Error',
                                      'El usuario o la contraseña son incorrectos',
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

    # Register window functions
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

    def create_new_user(self):
        print ("[INFO] Trying to create new user ...")

        if self.password_strength_check():
            username = unicode(self.ui.username_lineedit_reg.text())
            # username = username.strip().lower()
            password = unicode(self.ui.password_lineedit_reg.text())

            if (self.user_ddbb_connector.check_user(username) == True):  # The user already exist
                QMessageBox().information(self.focusWidget(), 'Error',
                                          'El nombre de usuario ya existe',
                                          QMessageBox.Ok)
                return False
            else:
                self.user_ddbb_connector.set_username_password(username, password)
                QMessageBox().information(self.focusWidget(), '',
                                          'Usuario creado correctamente',
                                          QMessageBox.Ok)

                self.user_ddbb_connector.load_users()  ##Reload the users
                completer = QCompleter(list_of_users)
                self.ui.username_lineedit.setCompleter(completer)
                self.ui.stackedWidget.setCurrentIndex(0)
                return True
        else:
            print ("[ERROR] The user couldn't be created ")
            return False

    def close_thsession_clicked(self):
        reply = QMessageBox.question(self.focusWidget(), '',
                                     ' Desea cerrar sesión?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mainMenu.setEnabled(False)
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.password_lineedit.clear()

    def goto_prevScreen(self):
        index = self.ui.stackedWidget.currentIndex()
        if (index != 0):
            index = index - 1
            if (index == 0):
                self.mainMenu.setEnabled(False)
            self.ui.stackedWidget.setCurrentIndex(index)
            self.ui.selplayer_combobox.setCurrentIndex(0)

    # Users window functions
    def deletegamefromlist(self):
        item_to_delete = self.ui.games_list.currentRow()
        self.ui.games_list.takeItem(item_to_delete)

    def selectedplayer_changed(self):
        self.selected_player_incombo = self.ui.selplayer_combobox.currentText()
        if (self.ui.selplayer_combobox.currentIndex() == 1):  # New player selected
            reply = QMessageBox.question(self.focusWidget(), '',
                                         ' Quiere añadir a un nuevo jugador?', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                self.ui.selplayer_combobox.setCurrentIndex(0)
                return False

            else:
                self.new_player_window()
                return True

    def selectediteminlist_changed(self):
        self.selected_game_inlist = self.ui.games_list.currentItem().text()
        print (self.ui.games_list.currentRow())

    def addgametolist(self):
        self.selected_game_incombo = self.ui.selgame_combobox.currentText()
        if self.selected_game_incombo != "":
            self.ui.games_list.addItem(self.selected_game_incombo)
            return True
        else:
            QMessageBox().information(self.focusWidget(), 'Error',
                                      'No se han seleccionado ningún juego',
                                      QMessageBox.Ok)
            return False

    def movelist_up(self):
        current_text = self.ui.games_list.currentItem().text()
        current_index = self.ui.games_list.currentRow()

        if current_index == 0: return
        new_index = current_index - 1
        previous_text = self.ui.games_list.item(new_index).text()

        print self.ui.games_list.item(new_index).text()

        self.ui.games_list.item(current_index).setText(previous_text)
        self.ui.games_list.item(new_index).setText(current_text)
        self.ui.games_list.setCurrentRow(new_index)

    def movelist_down(self):
        current_text = self.ui.games_list.currentItem().text()
        current_index = self.ui.games_list.currentRow()

        if current_index == self.ui.games_list.count() - 1: return
        new_index = current_index + 1
        previous_text = self.ui.games_list.item(new_index).text()

        print self.ui.games_list.item(new_index).text()

        self.ui.games_list.item(current_index).setText(previous_text)
        self.ui.games_list.item(new_index).setText(current_text)
        self.ui.games_list.setCurrentRow(new_index)

    def new_player_window(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def create_player(self):

        name = unicode(self.ui.name_player_lineedit.text())
        s1 = unicode(self.ui.surname1_player_lineedit.text())
        s2 = unicode(self.ui.surname2_player_lineedit.text())
        age = float(self.ui.age_player_lineedit.text())

        self.bbdd.new_patient(name, s1 + " " + s2)
        patients = self.bbdd.get_all_patients()
        new_list = []
        for p in patients:
            new_list.append(p.name + " " + p.surname)

        completer = QCompleter(new_list)

        last_element = new_list[-1]
        self.ui.selplayer_combobox.addItem(last_element)

        self.ui.selplayer_combobox.setCompleter(completer)
        self.ui.selplayer_combobox.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(2)

        self.ui.name_player_lineedit.clear()
        self.ui.surname1_player_lineedit.clear()
        self.ui.surname2_player_lineedit.clear()
        self.ui.age_player_lineedit.clear()

    @QtCore.Slot()
    def compute(self):
        return True

        #
        # metricsObtained
        #

    def metricsObtained(self, m):
        if self.currentGame.date is not None:
            self.aux_currentDate = datetime.strptime(m.currentDate, "%Y-%m-%dT%H:%M:%S.%f")
            self.currentGame.timePlayed = (self.aux_currentDate - self.currentGame.date).total_seconds() * 1000
            self.currentGame.touched = m.numScreenTouched
            self.currentGame.distance = 666  # calcular mas adelante
            self.currentGame.handClosed = m.numHandClosed
            self.currentGame.helps = m.numHelps
            self.currentGame.checks = m.numChecked
            self.currentGame.hits = m.numHits
            self.currentGame.fails = m.numFails

            self.updateUISig.emit(False)  # No ha habido cambio de estado
        else:
            print ("NO se ha iniciado el juego")

    #
    # statusChanged
    #
    def statusChanged(self, s):
        state_name = str(s.currentStatus.name)
        self.aux_currentStatus = state_name
        self.aux_currentDate = datetime.strptime(s.date, "%Y-%m-%dT%H:%M:%S.%f")

        self.updateUISig.emit(True)

        if state_name == "initializing":
            print "Initializing"
            self.currentSession.date = self.aux_currentDate

        if state_name == "ready":
            self.initGameSig.emit()

        if state_name == "paused":
            self.pausedGameSig.emit(s.date)

        if state_name == "wongame":
            self.endGameSig.emit(True, s.date)
        if state_name == "lostgame":
            self.endGameSig.emit(False, s.date)

        if state_name == "reseted":
            self.resetGameSig.emit()

        if state_name == "playing":
            self.playGameSig.emit(s.date)

        if state_name == "endsession":
            self.endSessionSig.emit(s.date)

    # Admin states

    def state_paused(self, date):
        currenttime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
        self.aux_datePaused = currenttime

        self.ui.continue_game_button.setEnabled(True);
        self.ui.reset_game_button.setEnabled(True);
        self.ui.pause_game_button.setEnabled(False);


    def state_ready(self):
        self.ui.start_game_button.setEnabled(True);
        self.ui.end_session_button.setEnabled(True);

        self.ui.status_label.setText(self.aux_currentStatus)
        self.ui.num_screentouched_label.setText("-")
        self.ui.num_closedhand_label.setText("-")
        self.ui.timeplayed_label.setText("-")
        self.ui.num_helps_label.setText("-")
        self.ui.num_checks_label.setText("-")
        self.ui.distance_label.setText("-")
        self.ui.num_hits_label.setText("-")
        self.ui.num_fails_label.setText("-")
        self.ui.date_label.setText("-")

    def state_playing(self, date):

        currenttime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")

        self.ui.start_game_button.setEnabled(False);
        self.ui.pause_game_button.setEnabled(True);
        self.ui.finish_game_button.setEnabled(True);
        self.ui.reset_game_button.setEnabled(False);
        self.ui.reset_game_button.setToolTip("Debe pausar el juego para poder reiniciarlo")
        self.ui.end_session_button.setEnabled(False);  # No se puede finalizar la sesion si hay un juego en marcha

        if self.currentGame.date is None:
            self.currentGame.date = currenttime

        if self.aux_datePaused is not None:
            self.ui.continue_game_button.setEnabled(False);
            self.ui.pause_game_button.setEnabled(True);
            time = currenttime - self.aux_datePaused
            self.currentGame.timePaused += time.total_seconds() * 1000
            self.aux_datePaused = None
            print "Time paused =  ", self.currentGame.timePaused, "milliseconds"

    def state_end_game(self, won, date):
        reply = QMessageBox.question(self.focusWidget(), 'Juego terminado',
                                     ' Desea guardar los datos del juego?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            currenttime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")

            self.currentGame.gameWon = won
            timeplayed = currenttime - self.currentGame.date
            self.currentGame.timePlayed = timeplayed.total_seconds() * 1000
            print "Time played =  ", self.currentGame.timePlayed, "milliseconds"

            self.currentSession.games.append(self.currentGame)

        self.currentGame = Game()

        self.list_games_toplay.pop(0)

        if len(self.list_games_toplay) == 0:
            print("No quedan juegos")
            self.admingame_proxy.adminEndSession()

        else:
            game = self.list_games_toplay[0]
            self.ui.info_game_label.setText(game)

            self.ui.pause_game_button.setEnabled(False);
            self.ui.continue_game_button.setEnabled(False);
            self.ui.finish_game_button.setEnabled(False);
            self.ui.reset_game_button.setEnabled(False);

            self.aux_datePaused = None

    def state_finish_session(self, date):
        reply = QMessageBox.question(self.focusWidget(), 'Juegos finalizados',
                                     ' Desea guardar los datos de la sesion actual?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            currenttime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")

            time = currenttime - self.currentSession.date
            self.currentSession.totaltime = time.total_seconds() * 1000
            print "Session time =  ", self.currentSession.totaltime, "milliseconds"

            self.compute_session_metrics()
            self.currentSession.save_session()
            self.sessions.append(self.currentSession)

        self.currentSession = Session()
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.selplayer_combobox.setCurrentIndex(0)
        self.ui.selgame_combobox.setCurrentIndex(0)
        self.ui.games_list.clear()

    def state_reset_game(self):

        self.ui.pause_game_button.setEnabled(False);
        self.ui.continue_game_button.setEnabled(False);
        self.ui.finish_game_button.setEnabled(False);
        self.ui.reset_game_button.setEnabled(False);
        self.ui.start_game_button.setEnabled(False);
        self.ui.end_session_button.setEnabled(False);

        self.aux_datePaused = None

        self.currentGame = Game()

    def compute_session_metrics(self):
        for game in self.currentSession.games:
            self.currentSession.totalHelps += game.helps
            self.currentSession.totalChecks += game.checks
            if game.gameWon:
                self.currentSession.wonGames += 1
            else:
                self.currentSession.lostGames += 1


    def updateUI(self, statusChange):
        self.ui.date_label.setText(self.currentGame.date.strftime("%c"))

        self.ui.status_label.setText(self.aux_currentStatus)

        self.ui.num_screentouched_label.setText(str(self.currentGame.touched))
        self.ui.num_closedhand_label.setText(str(self.currentGame.handClosed))
        self.ui.num_helps_label.setText(str(self.currentGame.helps))
        self.ui.num_checks_label.setText(str(self.currentGame.checks))
        self.ui.timeplayed_label.setText(str("{:.2f}".format(self.currentGame.timePlayed / 1000)) + " s")
        self.ui.distance_label.setText(str(self.currentGame.distance) + " mm")
        self.ui.num_hits_label.setText(str(self.currentGame.hits))
        self.ui.num_fails_label.setText(str(self.currentGame.fails))
