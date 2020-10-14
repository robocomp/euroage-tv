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
#

import sys, os, Ice

ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except:
	print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
	ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
	print('ROBOCOMP environment variable not set! Exiting.')
	sys.exit()


Ice.loadSlice("-I ./src/ --all ./src/AdminGame.ice")

from EuroAgeGamesAdmin import *

class AdminGameI(AdminGame):
	def __init__(self, worker):
		self.worker = worker

	def adminChangeLanguage(self, language, c):
		return self.worker.AdminGame_adminChangeLanguage(language)
	def adminContinueGame(self, c):
		return self.worker.AdminGame_adminContinueGame()
	def adminEndSession(self, c):
		return self.worker.AdminGame_adminEndSession()
	def adminPauseGame(self, c):
		return self.worker.AdminGame_adminPauseGame()
	def adminResetGame(self, c):
		return self.worker.AdminGame_adminResetGame()
	def adminStartGame(self, game, duration, c):
		return self.worker.AdminGame_adminStartGame(game, duration)
	def adminStartSession(self, player, c):
		return self.worker.AdminGame_adminStartSession(player)
	def adminStopApp(self, c):
		return self.worker.AdminGame_adminStopApp()
	def adminStopGame(self, c):
		return self.worker.AdminGame_adminStopGame()
