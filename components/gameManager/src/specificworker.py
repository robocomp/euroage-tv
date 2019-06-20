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
from passlib.hash import pbkdf2_sha256
from pprint import pprint

import passwordmeter
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QMessageBox, QCompleter, QAction, qApp

from admin_widgets import *
from genericworker import *

try:
    from bbdd import BBDD
except:
    print ("Database module not found")

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.Period = 2000
		self.timer.start(self.Period)

		self.admin_machine.start()

	def __del__(self):
		print 'SpecificWorker destructor'

	def setParams(self, params):
		#try:
		#	self.innermodel = InnerModel(params["InnerModelPath"])
		#except:
		#	traceback.print_exc()
		#	print "Error reading config params"
		return True


# =============== Slots methods for State Machine ===================
# ===================================================================
	#
	# sm_user_login
	#
	@QtCore.Slot()
	def sm_user_login(self):
		print("Entered state user_login")
		pass

	#
	# sm_admin_games
	#
	@QtCore.Slot()
	def sm_admin_games(self):
		print("Entered state admin_games")
		pass

	#
	# sm_create_player
	#
	@QtCore.Slot()
	def sm_create_player(self):
		print("Entered state create_player")
		pass

	#
	# sm_create_user
	#
	@QtCore.Slot()
	def sm_create_user(self):
		print("Entered state create_user")
		pass

	#
	# sm_game_end
	#
	@QtCore.Slot()
	def sm_game_end(self):
		print("Entered state game_end")
		pass

	#
	# sm_paused
	#
	@QtCore.Slot()
	def sm_paused(self):
		print("Entered state paused")
		pass

	#
	# sm_playing
	#
	@QtCore.Slot()
	def sm_playing(self):
		print("Entered state playing")
		pass

	#
	# sm_session_init
	#
	@QtCore.Slot()
	def sm_session_init(self):
		print("Entered state session_init")
		pass

	#
	# sm_wait_play
	#
	@QtCore.Slot()
	def sm_wait_play(self):
		print("Entered state wait_play")
		pass

	#
	# sm_wait_ready
	#
	@QtCore.Slot()
	def sm_wait_ready(self):
		print("Entered state wait_ready")
		pass

	#
	# sm_session_end
	#
	@QtCore.Slot()
	def sm_session_end(self):
		print("Entered state session_end")
		pass


# =================================================================
# =================================================================


	#
	# metricsObtained
	#
	def metricsObtained(self, m):
		#
		#subscribesToCODE
		#
		pass


	#
	# statusChanged
	#
	def statusChanged(self, s):
		#
		#subscribesToCODE
		#
		pass

