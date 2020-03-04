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

import csv
import json
import math
import os
from datetime import datetime
import sys


import bcrypt
from PySide2.QtGui import QKeySequence
from pprint import pprint

import passwordmeter
from PySide2.QtCore import Signal, QObject, Qt, QTranslator
from PySide2.QtWidgets import QMessageBox, QCompleter, QAction, qApp, QApplication, QShortcut, QListWidgetItem

from admin_widgets import *
from genericworker import *
from history import History

from src.widgets.QUserManager import QUserManager

try:
    from bbdd import BBDD
except:
    print("Database module not found")
    exit(1)

FILE_PATH = os.path.abspath(__file__)
CURRENT_PATH = os.path.dirname(__file__)

list_of_users = []


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


class Session:
    def __init__(self, patient, therapist):
        self.date = datetime.now()
        self.patient = patient
        self.therapist = therapist
        self.total_time = 0
        self.games = []
        self.num_games = 0
        self.total_helps = 0
        self.total_checks = 0
        self.won_games = 0
        self.lost_games = 0
        self.current_game = None

    def save_session(self):

        saving_dir = os.path.join(CURRENT_PATH, "../savedSessions")
        print("Saving session in ", saving_dir)

        if not os.path.isdir(saving_dir):
            os.mkdir(saving_dir)

        patient = self.patient.replace(" ", "").strip()
        patient_dir = os.path.join(saving_dir, patient)

        if not os.path.isdir(patient_dir):
            os.mkdir(patient_dir)

        date = datetime.strftime(self.date, "%y%m%d_%H%M%S")
        date_dir = os.path.join(patient_dir, date)

        if os.path.isdir(date_dir):
            print("Error, la sesion ya ha sido guardada")
            return
        else:
            os.mkdir(date_dir)

            for game in self.games:
                game.save_game(date_dir)

            rows = [
                ['tiempo total', 'num juegos', 'num ayudas', 'num comprobaciones', 'juegos ganados', 'juegos perdidos'],
                [self.total_time, len(self.games), self.total_helps, self.total_checks, self.won_games, self.lost_games]]

            filename = os.path.join(date_dir, "resumeSession" + ".csv")

            with open(filename, 'w') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerows(rows)
            csvFile.close()

    def save_session_to_ddbb(self, ddbb):

        print("Saving session in ")

        date = datetime.strftime(self.date, "%Y%m%d %H%M%S")
        result, session = ddbb.new_session(start=self.date, end=datetime.now(), patient=self.patient, therapist=self.therapist)
        if result:
            for game in self.games:
                game.session_id = session.id
                game.save_game_to_ddbb(ddbb=ddbb)


class Metrics:
    """
    Class to encapsulate the information of a metrics of a played game
    """
    def __init__(self):
        self.time = None
        self.distance = 0
        self.touched = 0
        self.handClosed = 0
        self.helps = 0
        self.checks = 0
        self.hits = 0
        self.fails = 0


class Game:
    """
    Class to encapsulate the information of a Game
    """
    def __init__(self):
        self.game_id = None
        self.name = ""
        self.start_time = datetime.now()
        self.end_time = None
        self.time_played = 0
        self.time_paused = 0
        self.metrics = []
        self.game_won = False
        self.session_id = None



    def save_game(self, output_dir):
        """
        Save the information of a game to a dir/file
        :param output_dir: dir to save th information of a game
        :return: --
        """
        name = self.name
        filename = os.path.join(output_dir, name.replace(" ", "").strip().lower() + ".csv")
        date = datetime.strftime(self.start_time, "%H:%M:%S")

        rows = [['hora comienzo', 'tiempo total', 'tiempo pausado', 'distancia recorrida', 'num pantalla pulsada',
                 'num mano cerrada', 'num ayudas', 'num comprobaciones', 'aciertos', 'fallos', 'juego ganado']]

        for m in self.metrics:
            rows.append([date, self.time_played, self.time_paused, m.distance, m.touched, m.handClosed, m.helps,
                         m.checks, m.hits, m.fails, self.game_won])

        with open(filename, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(rows)
        csvFile.close()

    def save_game_to_ddbb(self, ddbb):
        """
        Save the information of a game to a ddbb
        :param output_dir: ddbb object to save the information to
        :return: --
        """
        ddbb.new_round(name= self.name,
                       stime=self.start_time,
                       etime= self.end_time,
                       nwins=self.metrics[-1].checks,
                       nhelps=self.metrics[-1].helps,
                       ntouch=self.metrics[-1].touched,
                       distance=self.metrics[-1].distance,
                       result=self.game_won,
                       game_id=self.game_id,
                       hand_id="-1",
                       session_id=self.session_id)

    def end(self):
        """
        Store the time of the end of the game.
        :return: --
        """
        self.end_time = datetime.now()




class SpecificWorker(GenericWorker):
    login_executed = Signal(bool)
    updateUISig = Signal()

    def __init__(self, proxy_map):
        super(SpecificWorker, self).__init__(proxy_map)
        app = QApplication.instance()
        translator = QTranslator(app)
        if translator.load('src/i18n/pt_PT.qm'):
            print("-------Loading translation")
            if app is not None:
                print("-------Translating")
                result = app.installTranslator(translator)
            else:
                print("-------Could not find app instance")
        else:
            print("-------couldn't load translation")

        self.Period = 2000
        self.timer.start(self.Period)

        self.init_ui()
        self.setCentralWidget(self.ui)

        self.sessions = []
        self.__current_therapist = None
        self.current_session = None

        self.aux_sessionInit = False
        self.aux_datePaused = None
        self.aux_currentDate = None
        self.aux_currentStatus = None
        self.aux_wonGame = False
        self.aux_firtsGameInSession = True
        self.aux_reseted = False
        self.aux_prevPos = None
        self.aux_firstMetricReceived = True
        self.aux_savedGames = False
        self.__ready_session_received = False

        # TODO: Move to the session. Should have a list of games to play and played games.
        self.list_games_toplay = []

        self.ddbb = BBDD()
        self.ddbb.open_database("/home/robocomp/robocomp/components/euroage-tv/components/bbdd/prueba1.db")
        self.user_login_manager = QUserManager(ddbb=self.ddbb)
        self.history = History(self.ddbb, self)


        self.updateUISig.connect(self.updateUI)

        self.manager_machine.start()

    @property
    def current_game(self):
        """
        Getter for the current game of the current session
        :return: game of the current session
        """
        if self.current_session is not None:
            return self.current_session.current_game
        else:
            return None

    @current_game.setter
    def current_game(self, the_game):
        """
        Setter for the current game of the current session
        :return: game of the current session
        """
        if self.current_session is not None:
            self.current_session.current_game = the_game

    @property
    def current_therapist(self):
        """
        Getter for the current therapis of the current session
        Current Therapist can exists without a current session while this is being created.
        :return: therapist of the current session
        """
        if self.current_session is not None:
            return self.current_session.therapist
        else:
            return self.__current_therapist


    @current_therapist.setter
    def current_therapist(self, therapist):
        """
        Setter for the current therapist of the current session
        :return: game of the current session
        """
        if self.current_session is not None:
            self.current_session.therapist = therapist
        else:
            self.__current_therapist = therapist

    def init_ui(self):
        """
        Registers the custom widgets of the UI
        Load the main UI from .ui file
        Configure the actions of the menu, shortcuts and connect the signals
        :return:
        """
        loader = QUiLoader()
        loader.registerCustomWidget(LoginWindow)
        loader.registerCustomWidget(RegisterWindow)
        loader.registerCustomWidget(UsersWindow)
        loader.registerCustomWidget(PlayersWindow)
        loader.registerCustomWidget(GameWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/gameManager/src/uis/stackedUI.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        file.close()

        # Menu
        self.mainMenu = self.menuBar()
        fileMenu = self.mainMenu.addMenu('&Menú')
        if self.ui.stackedWidget.currentIndex == 0 or self.ui.stackedWidget.currentIndex == 1:
            self.mainMenu.setEnabled(False)

        exitAction = QAction('&Salir', self)
        exitAction.triggered.connect(self.t_admin_to_app_end)
        QApplication.instance().aboutToQuit.connect(self.t_admin_to_app_end)
        fileMenu.addAction(exitAction)

        # closeAction = QAction('&Cerrar sesión', self)
        # closeAction.triggered.connect(self.close_thsession_clicked)
        # fileMenu.addAction(closeAction)

        # Login window
        self.loginShortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.loginShortcut.activated.connect(self.check_login)
        self.ui.login_button_2.clicked.connect(self.check_login)
        self.ui.newuser_button_2.clicked.connect(self.t_user_login_to_create_user.emit)

        # Register window
        self.ui.password_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.password_2_lineedit_reg.textChanged.connect(self.password_strength_check)
        self.ui.createuser_button_reg.clicked.connect(self.create_new_user)
        self.ui.back_button_reg.clicked.connect(self.t_create_user_to_user_login.emit)

        ## User window
        self.ui.selplayer_combobox.currentIndexChanged.connect(self.selected_player_changed)
        self.ui.history_button.clicked.connect(self.view_history_clicked)
        self.ui.addgame_button.clicked.connect(self.add_game_to_list)
        self.ui.deletegame_button.clicked.connect(self.delete_game_from_list)
        self.ui.up_button.clicked.connect(self.move_list_up)
        self.ui.down_button.clicked.connect(self.move_list_down)
        self.ui.startsession_button.clicked.connect(self.start_session)
        self.all_games_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        self.all_games_shortcut.activated.connect(self.add_all_games_to_list)

        # New Player window
        self.ui.back_player_button.clicked.connect(self.t_create_player_to_session_init.emit)
        self.ui.create_player_button.clicked.connect(self.create_player)

        # Game window
        self.ui.start_game_button.clicked.connect(self.start_clicked)
        self.ui.pause_game_button.clicked.connect(self.pause_clicked)
        self.ui.continue_game_button.clicked.connect(self.continue_clicked)
        self.ui.finish_game_button.clicked.connect(self.finish_clicked)
        self.ui.reset_game_button.clicked.connect(self.reset_clicked)
        self.ui.end_session_button.clicked.connect(self.end_session_clicked)

        self.ui.quit_button.clicked.connect(self.t_admin_to_app_end)

    def ddbb_status_changed(self, string):
        """
        Slot to show status changes on the UI.
        :param string:
        :return:
        """
        self.ui.login_status.setText(string)

    # Login window functions
    def check_login(self):
        """
        Checks login from DDBB and update the state and UI.
        """
        print("[INFO] Checking login ...")

        username = unicode(self.ui.username_lineedit.text())
        # username = username.strip().lower() ##The username is stored and checked in lower case
        password = unicode(self.ui.password_lineedit.text())

        if self.user_login_manager.check_user_password(username, password):
            self.current_therapist = self.ddbb.get_therapist_by_username(username)
            self.loginShortcut.activated.disconnect(self.check_login)
            self.login_executed.emit(True)
            self.t_user_login_to_session_init.emit()

        else:
            MyQMessageBox.information(self.focusWidget(), 'Error',
                                      self.tr('El usuario o la contraseña son incorrectos'),
                                      QMessageBox.Ok)

    def update_login_status(self, status):
        """
        Slot to update the state on the login window"
        :param status: True if logged in ok.
        """""
        if not status:
            self.ui.login_status.setText("[!]Login failed")
        else:
            self.ui.login_status.setText("[+]Login OK")


    # Register window functions
    def password_strength_check(self):
        """
        Checks the strength of the password inserted on the user registration ui and update the information
        """
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
        """
        Checks password strength, check if user already exists, create the new user and change the corresponding state
        :return: False if failed, True if user is created.
        """
        print("[INFO] Trying to create new user ...")

        if self.password_strength_check():
            username = unicode(self.ui.username_lineedit_reg.text())
            # username = username.strip().lower()
            password = unicode(self.ui.password_lineedit_reg.text())

            if self.user_login_manager.check_user(username) == True:  # The user already exist
                QMessageBox().information(self.focusWidget(), 'Error',
                                          self.tr('El nombre de usuario ya existe'),
                                          QMessageBox.Ok)
                return False
            else:
                self.user_login_manager.set_username_password(username, password)
                MyQMessageBox.information(self.focusWidget(), '',
                                          self.tr('Usuario creado correctamente'),
                                          QMessageBox.Ok)


                completer = QCompleter(list_of_users)
                self.ui.username_lineedit.setCompleter(completer)

                self.t_create_user_to_user_login.emit()
                return True
        else:
            print("[ERROR] The user couldn't be created ")
            return False


    def delete_game_from_list(self):
        """
        Delete the current selected game from the list of games to play.
        :return:
        """
        item_to_delete = self.ui.games_list.currentRow()
        self.ui.games_list.takeItem(item_to_delete)

    def selected_player_changed(self):
        """
        Slot to manage creation of new users/patients
        :return:
        """
        if self.ui.selplayer_combobox.currentIndex() == 1:  # New player selected
            reply = MyQMessageBox.question(self.focusWidget(), '',
                                         self.tr('¿Quiere añadir a un nuevo jugador?'), QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                self.ui.selplayer_combobox.setCurrentIndex(0)
                return False

            else:
                self.t_session_init_to_create_player.emit()
                return True

    def view_history_clicked(self):
        self.history.initialize()
        self.history.showMaximized()
        patient_username = self.ui.selplayer_combobox.currentText()
        if patient_username != "":
            self.history.set_selected_patient(patient_username)

    def add_game_to_list(self):
        """
        Slot to add a game to the list of games to play in the session
        :return:
        """

        selected_game_incombo = self.ui.selgame_combobox.currentData()
        selected_name_incombo = self.ui.selgame_combobox.currentText()
        if selected_game_incombo is not None:
            from widgets.CustomQTimeEdit import CustomTimeEditDialog
            time_widget = CustomTimeEditDialog(self)
            if time_widget.exec_():
            item = QListWidgetItem(selected_name_incombo)
                selected_game_incombo.duration = time_widget.seconds
            item.setData(Qt.UserRole, selected_game_incombo)
            self.ui.games_list.addItem(item)
            self.ui.selgame_combobox.setCurrentIndex(0)
            return True
        else:
            MyQMessageBox.information(self.focusWidget(), 'Error',
                                      self.tr('No se ha seleccionado ningún juego'),
                                      QMessageBox.Ok)
            return False

    def add_all_games_to_list(self):
        """
        Slot to add a game to the list of games to play in the session
        :return:
        """
        for index in range(self.ui.selgame_combobox.count()):
            next_value_in_combo = self.ui.selgame_combobox.itemText(index)
            if next_value_in_combo != "":
                self.ui.games_list.addItem(next_value_in_combo)
        self.ui.selgame_combobox.setCurrentIndex(0)


    def move_list_up(self):
        """
        Move an item of the list of games to play up in the list
        """
        current_text = self.ui.games_list.currentItem().text()
        current_index = self.ui.games_list.currentRow()

        if current_index == 0: return
        new_index = current_index - 1
        previous_text = self.ui.games_list.item(new_index).text()

        print(self.ui.games_list.item(new_index).text())

        self.ui.games_list.item(current_index).setText(previous_text)
        self.ui.games_list.item(new_index).setText(current_text)
        self.ui.games_list.setCurrentRow(new_index)

    def move_list_down(self):
        """
        Move an item of the list of games to play down in the list
        """
        current_text = self.ui.games_list.currentItem().text()
        current_index = self.ui.games_list.currentRow()

        if current_index == self.ui.games_list.count() - 1: return
        new_index = current_index + 1
        previous_text = self.ui.games_list.item(new_index).text()

        print(self.ui.games_list.item(new_index).text())

        self.ui.games_list.item(current_index).setText(previous_text)
        self.ui.games_list.item(new_index).setText(current_text)
        self.ui.games_list.setCurrentRow(new_index)

    # New player
    def create_player(self):
        """
        Create a new user on the DDBB from the information introduced on the UI.
        """
        username = str(self.ui.username_player_lineedit.text())
        nombre = str(self.ui.nombre_player_lineedit.text())
        sexo = str(self.ui.sexo_player_lineedit.text())
        edad = float(self.ui.edad_player_lineedit.text())

        patient = self.ddbb.new_patient(username=username, nombre=nombre, sexo=sexo, edad=edad, profesional=self.current_therapist.id_terapeuta)
        # update the players show on the ui
        patients = self.ddbb.get_all_patients_by_therapist(self.current_therapist.id_terapeuta)
        completer = QCompleter([patient.username for patient in patients])
        self.ui.selplayer_combobox.addItem(patient.username)
        self.ui.selplayer_combobox.setCompleter(completer)
        self.t_create_player_to_session_init.emit()

    # Game window functions
    def start_clicked(self):
        """
        Slot to send the adminStartGame command to the game
        """
        self.admingame_proxy.adminStartGame(self.current_game.name, self.current_game.duration)

    def pause_clicked(self):
        """
        Slot to send the adminPauseGame command to the game
        """
        self.admingame_proxy.adminPauseGame()

    def continue_clicked(self):
        """
        Slot to send the adminContinueGame command to the game
        """
        self.admingame_proxy.adminContinueGame()

    def finish_clicked(self):
        """
        Slot to send the adminStopGame command to the game
        """
        reply = MyQMessageBox.question(self.focusWidget(), '',
                                     self.tr('¿Desea finalizar juego?'), QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminStopGame()

    def reset_clicked(self):
        """
        Slot to send the adminResetGame command to the game
        """
        reply = MyQMessageBox.question(self.focusWidget(), '',
                                     self.tr('¿Desea volver a empezar? Los datos del juego no se guardarán'), QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminResetGame()

    def start_session(self):
        """
        Slot to create the Session, send the adminStartSession command with the selected player/patient and configure
        the list of games to play.
        """
        patient = self.ui.selplayer_combobox.currentData()
        player_name = patient.username
        self.list_games_toplay = []

        for index in range(self.ui.games_list.count()):
            self.list_games_toplay.append(self.ui.games_list.item(index).data(Qt.UserRole))

        if player_name == "":
            MyQMessageBox.information(self.focusWidget(), 'Error',
                                      self.tr('No se ha seleccionado ningun jugador'),
                                      QMessageBox.Ok)
        elif len(self.list_games_toplay) == 0:
            MyQMessageBox.information(self.focusWidget(), 'Error',
                                      self.tr('No se ha seleccionado ningún juego'),
                                      QMessageBox.Ok)
        else:

            self.current_session = Session(therapist=self.current_therapist.id_terapeuta, patient=str(patient.id_paciente))
            self.admingame_proxy.adminStartSession(player_name)

    def end_session_clicked(self):
        """
        Slot to finish the current session and send the adminEndSession command to the game.
        """
        reply = MyQMessageBox.question(self.focusWidget(), '',
                                     self.tr('¿Desea finalizar la sesión?'), QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.admingame_proxy.adminEndSession()

    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        return True

    # =============== Slots methods for State Machine ===================
    # ===================================================================
    #
    # sm_admin
    #
    @QtCore.Slot()
    def sm_admin(self):
        """
        admin => app_end
        :return:
        """
        print("Entered state admin")
        pass

    #
    # sm_app_end
    #
    @QtCore.Slot()
    def sm_app_end(self):
        print("Entered state app_end")
        # TODO: send command to end game
        self.admingame_proxy.adminStopApp()
        qApp.quit()
        pass

    #
    # sm_user_login
    #
    @QtCore.Slot()
    def sm_user_login(self):
        """
        user_login => create_user,session_init;
        create_user => user_login;
        :return:
        """
        print("Entered state user_login")

        self.ui.stackedWidget.setCurrentIndex(0)
        completer = QCompleter(list_of_users)
        self.ui.username_lineedit.setCompleter(completer)
        self.login_executed.connect(self.update_login_status)

    #
    # sm_create_player
    #
    @QtCore.Slot()
    def sm_create_player(self):
        """
        create_player => session_init;
        session_init => create_player;
        :return:
        """
        print("Entered state create_player")
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.username_player_lineedit.clear()
        self.ui.nombre_player_lineedit.clear()
        self.ui.sexo_player_lineedit.clear()
        self.ui.edad_player_lineedit.clear()

    #
    # sm_create_user
    #
    @QtCore.Slot()
    def sm_create_user(self):
        """
        user_login => create_user;
        create_user => user_login;
        :return:
        """
        print("Entered state create_user")
        self.ui.stackedWidget.setCurrentIndex(1)

    #
    # sm_game_end
    #
    @QtCore.Slot()
    def sm_game_end(self):
        """
        game_end => admin_games;
        playing => game_end;
        paused => game_end;
        :return:
        """
        print("Entered state game_end")

        reply = MyQMessageBox.question(self.focusWidget(), 'Juego terminado',
                                     self.tr('¿Desea guardar los datos del juego?'), QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_game.end()
            self.current_game.game_won = self.aux_wonGame
            self.aux_savedGames = True
            timeplayed = self.aux_currentDate - self.current_game.start_time
            self.current_game.time_played = timeplayed.total_seconds() * 1000
            print("Time played =  ", self.current_game.time_played, "milliseconds")

            self.current_session.games.append(self.current_game)

        self.aux_datePaused = None
        self.aux_wonGame = False
        self.aux_prevPos = None
        self.aux_firstMetricReceived = True

        self.current_game = None


        self.t_game_end_to_admin_games.emit()

    #
    # sm_paused
    #
    @QtCore.Slot()
    def sm_paused(self):
        """
        playing => paused;
        paused => admin_games, playing, game_end;
        """
        print("Entered state paused")
        self.ui.continue_game_button.setEnabled(True)
        self.ui.reset_game_button.setEnabled(True)
        self.ui.pause_game_button.setEnabled(False)

        self.aux_datePaused = self.aux_currentDate

    #
    # sm_playing
    #
    @QtCore.Slot()
    def sm_playing(self):
        """
        playing => paused, game_end;
        wait_play => playing;
        paused => playing;
        :return:
        """
        print("Entered state playing")
        self.ui.start_game_button.setEnabled(False)
        self.ui.pause_game_button.setEnabled(True)
        self.ui.finish_game_button.setEnabled(True)
        self.ui.reset_game_button.setEnabled(False)
        self.ui.reset_game_button.setToolTip("Debe pausar el juego para poder reiniciarlo")
        self.ui.end_session_button.setEnabled(False)  # No se puede finalizar la sesion si hay un juego en marcha
        self.ui.end_session_button.setToolTip("Debe finalizar el juego para poder terminar la sesión")

        if self.current_session.current_game.start_time is None:
            self.current_session.current_game.start_time = self.aux_currentDate

        if self.aux_datePaused is not None:
            self.ui.continue_game_button.setEnabled(False);
            self.ui.pause_game_button.setEnabled(True);
            time = self.aux_currentDate - self.aux_datePaused
            self.current_session.current_game.time_paused += time.total_seconds() * 1000
            self.aux_datePaused = None
            print("Time paused =  ", self.current_session.current_game.time_paused, "milliseconds")

    #
    # sm_session_init
    #
    @QtCore.Slot()
    def sm_session_init(self):
        """
        session_init => create_player, wait_ready;
        user_login => session_init;
        create_player => session_init;
	    session_end => session_init;
        :return:
        """
        print("Entered state session_init")
        self.ui.stackedWidget.setCurrentIndex(2)

        self.ui.selplayer_combobox.setCurrentIndex(0)
        self.ui.selgame_combobox.setCurrentIndex(0)

        if self.aux_sessionInit == False:

            patients = self.ddbb.get_all_patients_by_therapist(self.current_therapist.id_terapeuta)
            patients_list = []
            for p in patients:
                self.ui.selplayer_combobox.addItem(p.username, p)


            for game in self.ddbb.get_all_games():
                translated_name = QObject().tr(game.name)
                self.ui.selgame_combobox.addItem(translated_name, game)


            self.aux_sessionInit = True

        self.ui.games_list.clear()
        self.mainMenu.setEnabled(True)
        self.aux_savedGames = False

    def get_all_games_names(self):
        all_ddbb_games = self.ddbb.get_all_games()
        list_of_games = []
        for p in all_ddbb_games:
            list_of_games.append(p.name)
        return list_of_games


    #
    # sm_admin_games
    #
    @QtCore.Slot()
    def sm_admin_games(self):
        """
        admin_games => wait_play, session_end;
        wait_ready => admin_games;
        paused => admin_games;
        game_end => admin_games;
        :return:
        """
        print("Entered state admin_games")
        if len(self.list_games_toplay)>0:
            ddbb_game = self.list_games_toplay.pop(0)
            game_name = QObject().tr(ddbb_game.name)
            self.current_game = Game()
            self.current_game.game_id = ddbb_game.id
            self.current_game.name = ddbb_game.name
            self.current_game.duration = ddbb_game.duration
            self.ui.info_game_label.setText(game_name)
            if self.aux_firtsGameInSession or self.aux_reseted:
                self.aux_firtsGameInSession = False
                self.aux_reseted = False
        else:
            print("No quedan juegos")
            self.admingame_proxy.adminEndSession()

        self.ui.pause_game_button.setEnabled(False)
        self.ui.continue_game_button.setEnabled(False)
        self.ui.finish_game_button.setEnabled(False)
        self.ui.reset_game_button.setEnabled(False)

    #
    # sm_wait_play
    #
    @QtCore.Slot()
    def sm_wait_play(self):
        """
        wait_play => playing, session_end;
        admin_games => wait_play;
        :return:
        """
        print("Entered state wait_play")
        self.ui.start_game_button.setEnabled(True)
        self.ui.end_session_button.setEnabled(True)

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

    #
    # sm_wait_ready
    #
    @QtCore.Slot()
    def sm_wait_ready(self):
        """
        wait_ready => admin_games;
        session_init => wait_ready;
        :return:
        """
        print("Entered state wait_ready")
        self.ui.stackedWidget.setCurrentIndex(4)

        self.ui.start_game_button.setEnabled(False)
        self.ui.pause_game_button.setEnabled(False)
        self.ui.continue_game_button.setEnabled(False)
        self.ui.finish_game_button.setEnabled(False)
        self.ui.reset_game_button.setEnabled(False)
        self.ui.end_session_button.setEnabled(False)

        self.aux_firtsGameInSession = True

        MyQMessageBox.information(self.focusWidget(), 'Info',
                                  self.tr('Coloque la mano del paciente sobre la mesa. Cuando se haya detectado correctamente podrá empezar el juego'),
                                  QMessageBox.Ok)

        self.current_session.date = self.aux_currentDate

        # TODO: this is to fix a desincronization problem, need to be fixed with a better communication protocol between the State machines.
        if self.__ready_session_received:
            self.t_wait_ready_to_admin_games.emit()
            self.__ready_session_received = False

    #
    # sm_session_end
    #
    @QtCore.Slot()
    def sm_session_end(self):
        """
        session_end => session_init;
        admin_games => session_end;
        wait_play => session_end;
        :return:
        """
        print("Entered state session_end")

        if (self.aux_savedGames):
            reply = MyQMessageBox.question(self.focusWidget(), 'Juegos finalizados',
                                         self.tr('¿Desea guardar los datos de la sesion actual?'), QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                time = self.aux_currentDate - self.current_session.date
                self.current_session.total_time = time.total_seconds() * 1000
                print("Session time =  ", self.current_session.total_time, "milliseconds")

                self.compute_session_metrics()
                self.current_session.save_session_to_ddbb(self.ddbb)
                self.sessions.append(self.current_session)

        MyQMessageBox.information(self.focusWidget(), 'Adios',
                                  self.tr('Se ha finalizado la sesion'),
                                  QMessageBox.Ok)

        # exit(-1)
        self.t_session_end_to_session_init.emit()

    # =================================================================
    # =================================================================

    #
    # metricsObtained
    #
    def GameMetrics_metricsObtained(self, m):
        self.aux_currentDate = datetime.strptime(m.currentDate, "%Y-%m-%dT%H:%M:%S.%f")
        new_metrics = Metrics()
        new_metrics.time = self.aux_currentDate

        if self.current_game.start_time is not None:
            self.current_game.time_played = (self.aux_currentDate - self.current_game.start_time).total_seconds() * 1000
            new_metrics.touched = m.numScreenTouched
            new_metrics.handClosed = m.numHandClosed
            new_metrics.helps = m.numHelps
            new_metrics.checks = m.numChecked
            new_metrics.hits = m.numHits
            new_metrics.fails = m.numFails

            if self.aux_firstMetricReceived:
                new_metrics.distance = 0
                self.aux_firstMetricReceived = False
            else:
                if len(self.current_game.metrics) > 0:
                    # TODO: Review for a better checking of the initial position.
                    if m.pos.x != -1 and m.pos.y != -1 and self.aux_prevPos is None and self.current_game.metrics[-1].distance == 0:
                        print("Initial pos set")
                        self.aux_prevPos = m.pos
                    elif self.aux_prevPos is not None:
                        new_metrics.distance = (self.current_game.metrics[-1].distance + self.compute_distance_travelled(m.pos.x,m.pos.y))
                        self.aux_prevPos = m.pos

            self.current_game.metrics.append(new_metrics)
            self.updateUISig.emit()
        else:
            print("NO se ha iniciado el juego")

    #
    # statusChanged
    #
    def GameMetrics_statusChanged(self, s):
        state_name = str(s.currentStatus.name)
        self.aux_currentStatus = state_name
        self.aux_currentDate = datetime.strptime(s.date, "%Y-%m-%dT%H:%M:%S.%f")

        if state_name == "initializingSession":
            self.t_session_init_to_wait_ready.emit()

        if state_name == "readySession":
            # TODO: Patch to resolve a problem of desincronization if this arrives before this SM is in the wait_ready state
            self.__ready_session_received = True
            self.t_wait_ready_to_admin_games.emit()

        if state_name == "waitingGame":
            self.t_admin_games_to_wait_play.emit()

        if state_name == "playingGame":
            self.t_wait_play_to_playing.emit()
            self.t_paused_to_playing.emit()
            self.updateUISig.emit()

        if state_name == "pausedGame":
            self.t_playing_to_paused.emit()

        if state_name == "wonGame":
            self.activateWindow()
            self.aux_wonGame = True
            self.t_playing_to_game_end.emit()
            self.t_paused_to_game_end.emit()

        if state_name == "lostGame":
            self.activateWindow()
            self.aux_wonGame = False
            self.t_playing_to_game_end.emit()
            self.t_paused_to_game_end.emit()

        if state_name == "resetedGame":
            self.aux_reseted = True
            self.t_paused_to_admin_games.emit()
        #
        if state_name == "endSession":
            self.activateWindow()
            self.t_admin_games_to_session_end.emit()
            self.t_wait_play_to_session_end.emit()

    def compute_distance_travelled(self, x, y):
        """
        Calculate the mm
        :param x: New position x coord
        :param y: New position y coord
        :return: Distance from last point to the new point calculated as mm
        """
        prev_x = self.aux_prevPos.x
        prev_y = self.aux_prevPos.y
        travelled_pixels = math.sqrt(((x - prev_x) ** 2) + ((y - prev_y) ** 2))
        # Translating pixels to mm
        # TODO: move this to configuration file. It will depends on tv resolution and size
        screen_width_resolution = 1920
        screen_width_mm = 1100
        result = int(travelled_pixels * screen_width_mm / screen_width_resolution)
        return result

    def compute_session_metrics(self):
        for game in self.current_session.games:

            if game.game_won:
                self.current_session.won_games += 1
            else:
                self.current_session.lost_games += 1

            self.current_session.total_helps += game.metrics[-1].helps
            self.current_session.total_checks += game.metrics[-1].checks

    def updateUI(self):
        if self.current_game is not None and self.current_game.start_time is not None:
            self.ui.date_label.setText(self.current_game.start_time.strftime("%c"))

            self.ui.status_label.setText(self.aux_currentStatus)
            self.ui.timeplayed_label.setText(str("{:.3f}".format(self.current_game.time_played / 1000)) + " s")
            if len(self.current_game.metrics) > 0:
                self.ui.num_screentouched_label.setText(str(self.current_game.metrics[-1].touched))
                self.ui.num_closedhand_label.setText(str(self.current_game.metrics[-1].handClosed))
                self.ui.num_helps_label.setText(str(self.current_game.metrics[-1].helps))
                self.ui.num_checks_label.setText(str(self.current_game.metrics[-1].checks))
                self.ui.distance_label.setText(str("{:.3f}".format(self.current_game.metrics[-1].distance)) + " mm")
                self.ui.num_hits_label.setText(str(self.current_game.metrics[-1].hits))
                self.ui.num_fails_label.setText(str(self.current_game.metrics[-1].fails))
