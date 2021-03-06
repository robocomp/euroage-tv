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
import time

from genericworker import *

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 2000
		self.metrics = Metrics()
		self.first = True
		self.currentStatus = None
		self.timer.start(self.Period)

	def __del__(self):
		print 'SpecificWorker destructor'

	def setParams(self, params):
		testing = Status()
		testing.currentStatus = StatusType.waitingGame
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)


		return True

	@QtCore.Slot()
	def compute(self):
		if self.currentStatus == "playingGame":

			if self.first:
				self.metrics.currentDate = datetime.now().isoformat()
				self.metrics.numScreenTouched = 0
				self.metrics.numHandClosed = 0
				self.metrics.numHelps = 0
				self.metrics.numChecked = 0
				self.metrics.numHits = 0
				self.metrics.numFails = 0
				self.first = False

			else:
				self.metrics.currentDate = datetime.now().isoformat()
				self.metrics.numScreenTouched += 1
				self.metrics.numHandClosed += 1
				self.metrics.numHelps += 2
				self.metrics.numChecked += 1
				self.metrics.numHits += 3
				self.metrics.numFails += 1
			self.gamemetrics_proxy.metricsObtained (self.metrics)

		print 'SpecificWorker.compute...'
		return True

	#
	# adminContinue
	#
	def adminContinueGame(self):
		testing = Status()
		testing.currentStatus = StatusType.playingGame
		self.currentStatus = "playingGame"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Continue game"

	#
	# adminReset
	#
	def adminResetGame(self):
		testing = Status()
		testing.currentStatus = StatusType.resetedGame
		self.currentStatus = "resetedGame"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Reset game"

	#
	# adminStartGame
	#
	def adminStartGame(self, game):
		testing = Status()
		testing.currentStatus = StatusType.playingGame
		self.currentStatus = "playingGame"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Start game ", game

	#
	# adminPause
	#
	def adminPauseGame(self):
		testing = Status()
		testing.currentStatus = StatusType.pausedGame
		self.currentStatus = "pausedGame"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Pause game"

	#
	# adminStartSession
	#
	def adminStartSession(self, player):
		testing = Status()
		testing.currentStatus = StatusType.initializingSession
		self.currentStatus = "initializingSession"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Start session with ", player

	#
	# adminStop
	#
	def adminStopGame(self):
		testing = Status()
		testing.currentStatus = StatusType.wonGame
		self.currentStatus = "Stopped game"
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "Stop game"

	#
	# adminEndSession
	#
	def adminEndSession(self):
		testing = Status()
		testing.currentStatus = StatusType.endSession
		testing.date = datetime.now().isoformat()
		self.gamemetrics_proxy.statusChanged(testing)
		print "End session"

