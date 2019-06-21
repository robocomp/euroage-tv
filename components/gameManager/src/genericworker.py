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

import sys, Ice, os
from PySide2 import QtWidgets, QtCore

ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
	print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
	ROBOCOMP = '/opt/robocomp'

preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ --all /opt/robocomp/interfaces/"
Ice.loadSlice(preStr+"CommonBehavior.ice")
import RoboCompCommonBehavior

additionalPathStr = ''
icePaths = [ '/opt/robocomp/interfaces' ]
try:
	SLICE_PATH = os.environ['SLICE_PATH'].split(':')
	for p in SLICE_PATH:
		icePaths.append(p)
		additionalPathStr += ' -I' + p + ' '
	icePaths.append('/opt/robocomp/interfaces')
except:
	print 'SLICE_PATH environment variable was not exported. Using only the default paths'
	pass

ice_AdminGame = False
for p in icePaths:
	if os.path.isfile(p+'/AdminGame.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"AdminGame.ice"
		Ice.loadSlice(wholeStr)
		ice_AdminGame = True
		break
if not ice_AdminGame:
	print 'Couln\'t load AdminGame'
	sys.exit(-1)
from EuroAgeGamesAdmin import *
ice_AdminGame = False
for p in icePaths:
	if os.path.isfile(p+'/AdminGame.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"AdminGame.ice"
		Ice.loadSlice(wholeStr)
		ice_AdminGame = True
		break
if not ice_AdminGame:
	print 'Couln\'t load AdminGame'
	sys.exit(-1)
from EuroAgeGamesAdmin import *


from gamemetricsI import *

try:
	from ui_mainUI import *
except:
	print "Can't import UI file. Did you run 'make'?"
	sys.exit(-1)


class GenericWorker(QtWidgets.QMainWindow):

	kill = QtCore.Signal()
#Signals for State Machine
	user_logintocreate_user = QtCore.Signal()
	user_logintosession_init = QtCore.Signal()
	create_usertouser_login = QtCore.Signal()
	session_inittocreate_player = QtCore.Signal()
	session_inittowait_ready = QtCore.Signal()
	create_playertosession_init = QtCore.Signal()
	wait_readytoadmin_games = QtCore.Signal()
	admin_gamestowait_play = QtCore.Signal()
	admin_gamestosession_end = QtCore.Signal()
	wait_playtoplaying = QtCore.Signal()
	wait_playtosession_end = QtCore.Signal()
	playingtopaused = QtCore.Signal()
	playingtogame_end = QtCore.Signal()
	pausedtoadmin_games = QtCore.Signal()
	pausedtoplaying = QtCore.Signal()
	pausedtogame_end = QtCore.Signal()
	game_endtoadmin_games = QtCore.Signal()

#-------------------------

	def __init__(self, mprx):
		super(GenericWorker, self).__init__()


		self.admingame_proxy = mprx["AdminGameProxy"]
		self.ui = Ui_guiDlg()
		self.ui.setupUi(self)
		self.show()

		
		self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
		self.Period = 30
		self.timer = QtCore.QTimer(self)

#State Machine
		self.admin_machine= QtCore.QStateMachine()
		self.create_user_state = QtCore.QState(self.admin_machine)
		self.session_init_state = QtCore.QState(self.admin_machine)
		self.create_player_state = QtCore.QState(self.admin_machine)
		self.wait_ready_state = QtCore.QState(self.admin_machine)
		self.admin_games_state = QtCore.QState(self.admin_machine)
		self.wait_play_state = QtCore.QState(self.admin_machine)
		self.playing_state = QtCore.QState(self.admin_machine)
		self.paused_state = QtCore.QState(self.admin_machine)
		self.game_end_state = QtCore.QState(self.admin_machine)
		self.user_login_state = QtCore.QState(self.admin_machine)

		self.session_end_state = QtCore.QFinalState(self.admin_machine)


#------------------
#Initialization State machine
		self.user_login_state.addTransition(self.user_logintocreate_user, self.create_user_state)
		self.user_login_state.addTransition(self.user_logintosession_init, self.session_init_state)
		self.create_user_state.addTransition(self.create_usertouser_login, self.user_login_state)
		self.session_init_state.addTransition(self.session_inittocreate_player, self.create_player_state)
		self.session_init_state.addTransition(self.session_inittowait_ready, self.wait_ready_state)
		self.create_player_state.addTransition(self.create_playertosession_init, self.session_init_state)
		self.wait_ready_state.addTransition(self.wait_readytoadmin_games, self.admin_games_state)
		self.admin_games_state.addTransition(self.admin_gamestowait_play, self.wait_play_state)
		self.admin_games_state.addTransition(self.admin_gamestosession_end, self.session_end_state)
		self.wait_play_state.addTransition(self.wait_playtoplaying, self.playing_state)
		self.wait_play_state.addTransition(self.wait_playtosession_end, self.session_end_state)
		self.playing_state.addTransition(self.playingtopaused, self.paused_state)
		self.playing_state.addTransition(self.playingtogame_end, self.game_end_state)
		self.paused_state.addTransition(self.pausedtoadmin_games, self.admin_games_state)
		self.paused_state.addTransition(self.pausedtoplaying, self.playing_state)
		self.paused_state.addTransition(self.pausedtogame_end, self.game_end_state)
		self.game_end_state.addTransition(self.game_endtoadmin_games, self.admin_games_state)


		self.create_user_state.entered.connect(self.sm_create_user)
		self.session_init_state.entered.connect(self.sm_session_init)
		self.create_player_state.entered.connect(self.sm_create_player)
		self.wait_ready_state.entered.connect(self.sm_wait_ready)
		self.admin_games_state.entered.connect(self.sm_admin_games)
		self.wait_play_state.entered.connect(self.sm_wait_play)
		self.playing_state.entered.connect(self.sm_playing)
		self.paused_state.entered.connect(self.sm_paused)
		self.game_end_state.entered.connect(self.sm_game_end)
		self.user_login_state.entered.connect(self.sm_user_login)
		self.session_end_state.entered.connect(self.sm_session_end)

		self.admin_machine.setInitialState(self.user_login_state)

#------------------

	@QtCore.Slot()
	def killYourSelf(self):
		rDebug("Killing myself")
		self.kill.emit()

	# \brief Change compute period
	# @param per Period in ms
	@QtCore.Slot(int)
	def setPeriod(self, p):
		print "Period changed", p
		Period = p
		timer.start(Period)
