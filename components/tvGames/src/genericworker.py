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

ice_GenericBase = False
for p in icePaths:
	if os.path.isfile(p+'/GenericBase.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"GenericBase.ice"
		Ice.loadSlice(wholeStr)
		ice_GenericBase = True
		break
if not ice_GenericBase:
	print 'Couln\'t load GenericBase'
	sys.exit(-1)
from RoboCompGenericBase import *
ice_TvGames = False
for p in icePaths:
	if os.path.isfile(p+'/TvGames.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"TvGames.ice"
		Ice.loadSlice(wholeStr)
		ice_TvGames = True
		break
if not ice_TvGames:
	print 'Couln\'t load TvGames'
	sys.exit(-1)
from RoboCompTvGames import *
ice_CameraSimple = False
for p in icePaths:
	if os.path.isfile(p+'/CameraSimple.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"CameraSimple.ice"
		Ice.loadSlice(wholeStr)
		ice_CameraSimple = True
		break
if not ice_CameraSimple:
	print 'Couln\'t load CameraSimple'
	sys.exit(-1)
from RoboCompCameraSimple import *
ice_TouchPoints = False
for p in icePaths:
	if os.path.isfile(p+'/TouchPoints.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"TouchPoints.ice"
		Ice.loadSlice(wholeStr)
		ice_TouchPoints = True
		break
if not ice_TouchPoints:
	print 'Couln\'t load TouchPoints'
	sys.exit(-1)
from RoboCompTouchPoints import *
ice_HandDetection = False
for p in icePaths:
	if os.path.isfile(p+'/HandDetection.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"HandDetection.ice"
		Ice.loadSlice(wholeStr)
		ice_HandDetection = True
		break
if not ice_HandDetection:
	print 'Couln\'t load HandDetection'
	sys.exit(-1)
from RoboCompHandDetection import *
ice_JointMotor = False
for p in icePaths:
	if os.path.isfile(p+'/JointMotor.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"JointMotor.ice"
		Ice.loadSlice(wholeStr)
		ice_JointMotor = True
		break
if not ice_JointMotor:
	print 'Couln\'t load JointMotor'
	sys.exit(-1)
from RoboCompJointMotor import *
ice_RGBD = False
for p in icePaths:
	if os.path.isfile(p+'/RGBD.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"RGBD.ice"
		Ice.loadSlice(wholeStr)
		ice_RGBD = True
		break
if not ice_RGBD:
	print 'Couln\'t load RGBD'
	sys.exit(-1)
from RoboCompRGBD import *
ice_CommonBehavior = False
for p in icePaths:
	if os.path.isfile(p+'/CommonBehavior.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"CommonBehavior.ice"
		Ice.loadSlice(wholeStr)
		ice_CommonBehavior = True
		break
if not ice_CommonBehavior:
	print 'Couln\'t load CommonBehavior'
	sys.exit(-1)
from RoboCompCommonBehavior import *
ice_GameMetrics = False
for p in icePaths:
	if os.path.isfile(p+'/GameMetrics.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"GameMetrics.ice"
		Ice.loadSlice(wholeStr)
		ice_GameMetrics = True
		break
if not ice_GameMetrics:
	print 'Couln\'t load GameMetrics'
	sys.exit(-1)
from EuroAgeGamesMetrics import *
ice_GetAprilTags = False
for p in icePaths:
	if os.path.isfile(p+'/GetAprilTags.ice'):
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"GetAprilTags.ice"
		Ice.loadSlice(wholeStr)
		ice_GetAprilTags = True
		break
if not ice_GetAprilTags:
	print 'Couln\'t load GetAprilTags'
	sys.exit(-1)
from RoboCompGetAprilTags import *
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
	session_start_waittosession_init = QtCore.Signal()
	session_inittogame_start_wait = QtCore.Signal()
	game_start_waittogame_init = QtCore.Signal()
	game_start_waittosession_end = QtCore.Signal()
	game_inittogame_loop = QtCore.Signal()
	game_looptogame_pause = QtCore.Signal()
	game_looptogame_won = QtCore.Signal()
	game_looptogame_lost = QtCore.Signal()
	game_looptogame_end = QtCore.Signal()
	game_wontogame_start_wait = QtCore.Signal()
	game_losttogame_start_wait = QtCore.Signal()
	game_pausetogame_loop = QtCore.Signal()
	game_pausetogame_reset = QtCore.Signal()
	game_endtogame_lost = QtCore.Signal()
	game_endtogame_won = QtCore.Signal()
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
		self.game_machine= QtCore.QStateMachine()
		self.session_init_state = QtCore.QState(self.game_machine)
		self.game_start_wait_state = QtCore.QState(self.game_machine)
		self.game_init_state = QtCore.QState(self.game_machine)
		self.game_loop_state = QtCore.QState(self.game_machine)
		self.game_pause_state = QtCore.QState(self.game_machine)
		self.game_reset_state = QtCore.QState(self.game_machine)
		self.game_end_state = QtCore.QState(self.game_machine)
		self.game_won_state = QtCore.QState(self.game_machine)
		self.game_lost_state = QtCore.QState(self.game_machine)
		self.session_start_wait_state = QtCore.QState(self.game_machine)

		self.session_end_state = QtCore.QFinalState(self.game_machine)



		self.player_acquisition_loop_state = QtCore.QState(self.session_init_state)
		self.player_acquisition_init_state = QtCore.QState(self.session_init_state)

		self.player_acquisition_ended_state = QtCore.QFinalState(self.session_init_state)


#------------------
#Initialization State machine
		self.session_start_wait_state.addTransition(self.session_start_waittosession_init, self.session_init_state)
		self.session_init_state.addTransition(self.session_inittogame_start_wait, self.game_start_wait_state)
		self.game_start_wait_state.addTransition(self.game_start_waittogame_init, self.game_init_state)
		self.game_start_wait_state.addTransition(self.game_start_waittosession_end, self.session_end_state)
		self.game_init_state.addTransition(self.game_inittogame_loop, self.game_loop_state)
		self.game_loop_state.addTransition(self.game_looptogame_pause, self.game_pause_state)
		self.game_loop_state.addTransition(self.game_looptogame_won, self.game_won_state)
		self.game_loop_state.addTransition(self.game_looptogame_lost, self.game_lost_state)
		self.game_loop_state.addTransition(self.game_looptogame_end, self.game_end_state)
		self.game_won_state.addTransition(self.game_wontogame_start_wait, self.game_start_wait_state)
		self.game_lost_state.addTransition(self.game_losttogame_start_wait, self.game_start_wait_state)
		self.game_pause_state.addTransition(self.game_pausetogame_loop, self.game_loop_state)
		self.game_pause_state.addTransition(self.game_pausetogame_reset, self.game_reset_state)
		self.game_end_state.addTransition(self.game_endtogame_lost, self.game_lost_state)
		self.game_end_state.addTransition(self.game_endtogame_won, self.game_won_state)
		self.game_reset_state.addTransition(self.game_resettogame_start_wait, self.game_start_wait_state)
		self.player_acquisition_init_state.addTransition(self.player_acquisition_inittoplayer_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.player_acquisition_looptoplayer_acquisition_loop, self.player_acquisition_loop_state)
		self.player_acquisition_loop_state.addTransition(self.player_acquisition_looptoplayer_acquisition_ended, self.player_acquisition_ended_state)


		self.session_init_state.entered.connect(self.sm_session_init)
		self.game_start_wait_state.entered.connect(self.sm_game_start_wait)
		self.game_init_state.entered.connect(self.sm_game_init)
		self.game_loop_state.entered.connect(self.sm_game_loop)
		self.game_pause_state.entered.connect(self.sm_game_pause)
		self.game_reset_state.entered.connect(self.sm_game_reset)
		self.game_end_state.entered.connect(self.sm_game_end)
		self.game_won_state.entered.connect(self.sm_game_won)
		self.game_lost_state.entered.connect(self.sm_game_lost)
		self.session_start_wait_state.entered.connect(self.sm_session_start_wait)
		self.session_end_state.entered.connect(self.sm_session_end)
		self.player_acquisition_init_state.entered.connect(self.sm_player_acquisition_init)
		self.player_acquisition_ended_state.entered.connect(self.sm_player_acquisition_ended)
		self.player_acquisition_loop_state.entered.connect(self.sm_player_acquisition_loop)

		self.game_machine.setInitialState(self.session_start_wait_state)
		self.session_init_state.setInitialState(self.player_acquisition_init_state)

#------------------

#Slots funtion State Machine
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
	def sm_session_start_wait(self):
		print "Error: lack sm_session_start_wait in Specificworker"
		sys.exit(-1)

	@QtCore.Slot()
	def sm_session_end(self):
		print "Error: lack sm_session_end in Specificworker"
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
