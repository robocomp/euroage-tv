#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 by YOUR NAME HERE
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
	print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
	ROBOCOMP = '/opt/robocomp'

Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")
import RoboCompCommonBehavior

Ice.loadSlice("-I ./src/ --all ./src/AdminGame.ice")
import EuroAgeGamesAdmin
Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")
import RoboCompCommonBehavior
Ice.loadSlice("-I ./src/ --all ./src/GameMetrics.ice")
import EuroAgeGamesMetrics
Ice.loadSlice("-I ./src/ --all ./src/TouchPoints.ice")
import RoboCompTouchPoints
Ice.loadSlice("-I ./src/ --all ./src/TvGames.ice")
import RoboCompTvGames


import admingameI
import commonbehaviorI
import tvgamesI


try:
	from ui_mainUI import *
except:
	print("Can't import UI file. Did you run 'make'?")
	sys.exit(-1)


class GenericWorker(QtWidgets.QWidget):

	kill = QtCore.Signal()
#Signals for State Machine
	t_game_machine_to_app_end = QtCore.Signal()
	t_session_start_wait_to_session_init = QtCore.Signal()
	t_session_init_to_game_start_wait = QtCore.Signal()
	t_game_start_wait_to_game_start_wait = QtCore.Signal()
	t_game_start_wait_to_game_init = QtCore.Signal()
	t_game_start_wait_to_session_end = QtCore.Signal()
	t_session_end_to_session_start_wait = QtCore.Signal()
	t_game_init_to_game_loop = QtCore.Signal()
	t_game_loop_to_game_loop = QtCore.Signal()
	t_game_loop_to_game_pause = QtCore.Signal()
	t_game_loop_to_game_won = QtCore.Signal()
	t_game_loop_to_game_lost = QtCore.Signal()
	t_game_loop_to_game_end = QtCore.Signal()
	t_game_pause_to_game_loop = QtCore.Signal()
	t_game_pause_to_game_reset = QtCore.Signal()
	t_game_pause_to_game_resume = QtCore.Signal()
	t_game_pause_to_game_end = QtCore.Signal()
	t_game_resume_to_game_loop = QtCore.Signal()
	t_game_end_to_game_lost = QtCore.Signal()
	t_game_end_to_game_won = QtCore.Signal()
	t_game_lost_to_game_start_wait = QtCore.Signal()
	t_game_won_to_game_start_wait = QtCore.Signal()
	t_game_reset_to_game_start_wait = QtCore.Signal()
	t_player_acquisition_init_to_player_acquisition_loop = QtCore.Signal()
	t_player_acquisition_loop_to_player_acquisition_loop = QtCore.Signal()
	t_player_acquisition_loop_to_player_acquisition_ended = QtCore.Signal()

#-------------------------

	def __init__(self, mprx):
		super(GenericWorker, self).__init__()


		self.gamemetrics_proxy = mprx["GameMetricsPub"]
		self.touchpoints_proxy = mprx["TouchPointsPub"]
		self.ui = Ui_guiDlg()
		self.ui.setupUi(self)
		self.show()

		
		self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
		self.Period = 30
		self.timer = QtCore.QTimer(self)

#State Machine
		self.application_machine= QtCore.QStateMachine()
		self.game_machine_state = QtCore.QState(self.application_machine)

		self.app_end_state = QtCore.QFinalState(self.application_machine)



		self.session_init_state = QtCore.QState(self.game_machine_state)
		self.game_start_wait_state = QtCore.QState(self.game_machine_state)
		self.game_init_state = QtCore.QState(self.game_machine_state)
		self.game_loop_state = QtCore.QState(self.game_machine_state)
		self.game_pause_state = QtCore.QState(self.game_machine_state)
		self.game_resume_state = QtCore.QState(self.game_machine_state)
		self.game_reset_state = QtCore.QState(self.game_machine_state)
		self.game_end_state = QtCore.QState(self.game_machine_state)
		self.game_won_state = QtCore.QState(self.game_machine_state)
		self.game_lost_state = QtCore.QState(self.game_machine_state)
		self.session_end_state = QtCore.QState(self.game_machine_state)
		self.session_start_wait_state = QtCore.QState(self.game_machine_state)




		self.player_acquisition_loop_state = QtCore.QState(self.session_init_state)
		self.player_acquisition_init_state = QtCore.QState(self.session_init_state)

		self.player_acquisition_ended_state = QtCore.QFinalState(self.session_init_state)


#------------------
#Initialization State machine
		self.game_machine_state.addTransition(self.t_game_machine_to_app_end, self.app_end_state)
		self.session_start_wait_state.addTransition(self.t_session_start_wait_to_session_init, self.session_init_state)
		self.session_init_state.addTransition(self.t_session_init_to_game_start_wait, self.game_start_wait_state)
		self.game_start_wait_state.addTransition(self.t_game_start_wait_to_game_start_wait, self.game_start_wait_state)
		self.game_start_wait_state.addTransition(self.t_game_start_wait_to_game_init, self.game_init_state)
		self.game_start_wait_state.addTransition(self.t_game_start_wait_to_session_end, self.session_end_state)
		self.session_end_state.addTransition(self.t_session_end_to_session_start_wait, self.session_start_wait_state)
		self.game_init_state.addTransition(self.t_game_init_to_game_loop, self.game_loop_state)
		self.game_loop_state.addTransition(self.t_game_loop_to_game_loop, self.game_loop_state)
		self.game_loop_state.addTransition(self.t_game_loop_to_game_pause, self.game_pause_state)
		self.game_loop_state.addTransition(self.t_game_loop_to_game_won, self.game_won_state)
		self.game_loop_state.addTransition(self.t_game_loop_to_game_lost, self.game_lost_state)
		self.game_loop_state.addTransition(self.t_game_loop_to_game_end, self.game_end_state)
		self.game_pause_state.addTransition(self.t_game_pause_to_game_loop, self.game_loop_state)
		self.game_pause_state.addTransition(self.t_game_pause_to_game_reset, self.game_reset_state)
		self.game_pause_state.addTransition(self.t_game_pause_to_game_resume, self.game_resume_state)
		self.game_pause_state.addTransition(self.t_game_pause_to_game_end, self.game_end_state)
		self.game_resume_state.addTransition(self.t_game_resume_to_game_loop, self.game_loop_state)
		self.game_end_state.addTransition(self.t_game_end_to_game_lost, self.game_lost_state)
		self.game_end_state.addTransition(self.t_game_end_to_game_won, self.game_won_state)
		self.game_lost_state.addTransition(self.t_game_lost_to_game_start_wait, self.game_start_wait_state)
		self.game_won_state.addTransition(self.t_game_won_to_game_start_wait, self.game_start_wait_state)
		self.game_reset_state.addTransition(self.t_game_reset_to_game_start_wait, self.game_start_wait_state)
		self.player_acquisition_init_state.addTransition(self.t_player_acquisition_init_to_player_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.t_player_acquisition_loop_to_player_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.t_player_acquisition_loop_to_player_acquisition_ended, self.player_acquisition_ended_state)


		self.game_machine_state.entered.connect(self.sm_game_machine)
		self.app_end_state.entered.connect(self.sm_app_end)
		self.session_start_wait_state.entered.connect(self.sm_session_start_wait)
		self.session_init_state.entered.connect(self.sm_session_init)
		self.game_start_wait_state.entered.connect(self.sm_game_start_wait)
		self.game_init_state.entered.connect(self.sm_game_init)
		self.game_loop_state.entered.connect(self.sm_game_loop)
		self.game_pause_state.entered.connect(self.sm_game_pause)
		self.game_resume_state.entered.connect(self.sm_game_resume)
		self.game_reset_state.entered.connect(self.sm_game_reset)
		self.game_end_state.entered.connect(self.sm_game_end)
		self.game_won_state.entered.connect(self.sm_game_won)
		self.game_lost_state.entered.connect(self.sm_game_lost)
		self.session_end_state.entered.connect(self.sm_session_end)
		self.player_acquisition_init_state.entered.connect(self.sm_player_acquisition_init)
		self.player_acquisition_ended_state.entered.connect(self.sm_player_acquisition_ended)
		self.player_acquisition_loop_state.entered.connect(self.sm_player_acquisition_loop)

		self.application_machine.setInitialState(self.game_machine_state)
		self.game_machine_state.setInitialState(self.session_start_wait_state)
		self.session_init_state.setInitialState(self.player_acquisition_init_state)

#------------------

#Slots funtion State Machine
	@QtCore.Slot()
	def sm_game_machine(self):
		print("Error: lack sm_game_machine in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_app_end(self):
		print("Error: lack sm_app_end in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_init(self):
		print("Error: lack sm_session_init in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_start_wait(self):
		print("Error: lack sm_game_start_wait in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_init(self):
		print("Error: lack sm_game_init in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_loop(self):
		print("Error: lack sm_game_loop in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_pause(self):
		print("Error: lack sm_game_pause in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_resume(self):
		print("Error: lack sm_game_resume in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_reset(self):
		print("Error: lack sm_game_reset in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_end(self):
		print("Error: lack sm_game_end in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_won(self):
		print("Error: lack sm_game_won in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_lost(self):
		print("Error: lack sm_game_lost in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_end(self):
		print("Error: lack sm_session_end in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_start_wait(self):
		print("Error: lack sm_session_start_wait in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_loop(self):
		print("Error: lack sm_player_acquisition_loop in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_init(self):
		print("Error: lack sm_player_acquisition_init in Specificworker")
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_ended(self):
		print("Error: lack sm_player_acquisition_ended in Specificworker")
		sys.exit(-1)


#-------------------------
	@QtCore.Slot()
	def killYourSelf(self):
		rDebug("Killing myself")
		self.kill.emit()

	# \brief Change compute period
	# @param per Period in ms
	@QtCore.Slot(int)
	def setPeriod(self, p):
		print("Period changed", p)
		self.Period = p
		self.timer.start(self.Period)
