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


from admingameI import *
from commonbehaviorI import *
from tvgamesI import *

try:
	from ui_mainUI import *
except:
	print "Can't import UI file. Did you run 'make'?"
	sys.exit(-1)


class GenericWorker(QtWidgets.QWidget):

	kill = QtCore.Signal()
#Signals for State Machine
	game_machinetoapp_end = QtCore.Signal()
	session_start_waittosession_init = QtCore.Signal()
	session_inittogame_start_wait = QtCore.Signal()
	game_start_waittogame_start_wait = QtCore.Signal()
	game_start_waittogame_init = QtCore.Signal()
	game_start_waittosession_end = QtCore.Signal()
	session_endtosession_start_wait = QtCore.Signal()
	game_inittogame_loop = QtCore.Signal()
	game_looptogame_loop = QtCore.Signal()
	game_looptogame_pause = QtCore.Signal()
	game_looptogame_won = QtCore.Signal()
	game_looptogame_lost = QtCore.Signal()
	game_looptogame_end = QtCore.Signal()
	game_wontogame_start_wait = QtCore.Signal()
	game_losttogame_start_wait = QtCore.Signal()
	game_pausetogame_loop = QtCore.Signal()
	game_pausetogame_reset = QtCore.Signal()
	game_pausetogame_resume = QtCore.Signal()
	game_pausetogame_end = QtCore.Signal()
	game_resumetogame_loop = QtCore.Signal()
	game_endtogame_lost = QtCore.Signal()
	game_endtogame_won = QtCore.Signal()
	game_losttogame_start_wait = QtCore.Signal()
	game_wontogame_start_wait = QtCore.Signal()
	game_resettogame_start_wait = QtCore.Signal()
	player_acquisition_inittoplayer_acquisition_loop = QtCore.Signal()
	player_acquisition_looptoplayer_acquisition_loop = QtCore.Signal()
	player_acquisition_looptoplayer_acquisition_ended = QtCore.Signal()

#-------------------------

	def __init__(self, mprx):
		super(GenericWorker, self).__init__()


		self.camerasimple_proxy = mprx["CameraSimpleProxy"]
		self.getapriltags_proxy = mprx["GetAprilTagsProxy"]
		self.handdetection_proxy = mprx["HandDetectionProxy"]
		self.rgbd_proxy = mprx["RGBDProxy"]
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
		self.game_machine_state.addTransition(self.game_machinetoapp_end, self.app_end_state)
		self.session_start_wait_state.addTransition(self.session_start_waittosession_init, self.session_init_state)
		self.session_init_state.addTransition(self.session_inittogame_start_wait, self.game_start_wait_state)
		self.game_start_wait_state.addTransition(self.game_start_waittogame_start_wait, self.game_start_wait_state)
		self.game_start_wait_state.addTransition(self.game_start_waittogame_init, self.game_init_state)
		self.game_start_wait_state.addTransition(self.game_start_waittosession_end, self.session_end_state)
		self.session_end_state.addTransition(self.session_endtosession_start_wait, self.session_start_wait_state)
		self.game_init_state.addTransition(self.game_inittogame_loop, self.game_loop_state)
		self.game_loop_state.addTransition(self.game_looptogame_loop, self.game_loop_state)
		self.game_loop_state.addTransition(self.game_looptogame_pause, self.game_pause_state)
		self.game_loop_state.addTransition(self.game_looptogame_won, self.game_won_state)
		self.game_loop_state.addTransition(self.game_looptogame_lost, self.game_lost_state)
		self.game_loop_state.addTransition(self.game_looptogame_end, self.game_end_state)
		self.game_won_state.addTransition(self.game_wontogame_start_wait, self.game_start_wait_state)
		self.game_lost_state.addTransition(self.game_losttogame_start_wait, self.game_start_wait_state)
		self.game_pause_state.addTransition(self.game_pausetogame_loop, self.game_loop_state)
		self.game_pause_state.addTransition(self.game_pausetogame_reset, self.game_reset_state)
		self.game_pause_state.addTransition(self.game_pausetogame_resume, self.game_resume_state)
		self.game_pause_state.addTransition(self.game_pausetogame_end, self.game_end_state)
		self.game_resume_state.addTransition(self.game_resumetogame_loop, self.game_loop_state)
		self.game_end_state.addTransition(self.game_endtogame_lost, self.game_lost_state)
		self.game_end_state.addTransition(self.game_endtogame_won, self.game_won_state)
		self.game_lost_state.addTransition(self.game_losttogame_start_wait, self.game_start_wait_state)
		self.game_won_state.addTransition(self.game_wontogame_start_wait, self.game_start_wait_state)
		self.game_reset_state.addTransition(self.game_resettogame_start_wait, self.game_start_wait_state)
		self.player_acquisition_init_state.addTransition(self.player_acquisition_inittoplayer_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.player_acquisition_looptoplayer_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.player_acquisition_looptoplayer_acquisition_ended, self.player_acquisition_ended_state)


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
	def sm_n(self):
		print "Error: lack sm_n in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_o(self):
		print "Error: lack sm_o in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_n(self):
		print "Error: lack sm_n in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_e(self):
		print "Error: lack sm_e in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_machine(self):
		print "Error: lack sm_game_machine in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_app_end(self):
		print "Error: lack sm_app_end in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_init(self):
		print "Error: lack sm_session_init in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_start_wait(self):
		print "Error: lack sm_game_start_wait in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_init(self):
		print "Error: lack sm_game_init in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_loop(self):
		print "Error: lack sm_game_loop in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_pause(self):
		print "Error: lack sm_game_pause in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_resume(self):
		print "Error: lack sm_game_resume in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_reset(self):
		print "Error: lack sm_game_reset in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_end(self):
		print "Error: lack sm_game_end in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_won(self):
		print "Error: lack sm_game_won in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_game_lost(self):
		print "Error: lack sm_game_lost in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_end(self):
		print "Error: lack sm_session_end in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_start_wait(self):
		print "Error: lack sm_session_start_wait in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_loop(self):
		print "Error: lack sm_player_acquisition_loop in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_init(self):
		print "Error: lack sm_player_acquisition_init in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_player_acquisition_ended(self):
		print "Error: lack sm_player_acquisition_ended in Specificworker"
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
		print "Period changed", p
		Period = p
		timer.start(Period)
