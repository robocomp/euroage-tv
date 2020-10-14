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
    raise RuntimeError('ROBOCOMP environment variable not set! Exiting.')

additionalPathStr = ''
icePaths = []
try:
	icePaths.append('/opt/robocomp/interfaces')
	SLICE_PATH = os.environ['SLICE_PATH'].split(':')
	for p in SLICE_PATH:
		icePaths.append(p)
		additionalPathStr += ' -I' + p + ' '
except:
	print('SLICE_PATH environment variable was not exported. Using only the default paths')
	pass

Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")

from RoboCompCommonBehavior import *

class CommonBehaviorI(CommonBehavior):
	def __init__(self, worker):
		self.worker = worker

	def getParameterList(self, c):
		return self.worker.CommonBehavior_getParameterList()
	def getPeriod(self, c):
		return self.worker.CommonBehavior_getPeriod()
	def getState(self, c):
		return self.worker.CommonBehavior_getState()
	def killYourSelf(self, c):
		return self.worker.CommonBehavior_killYourSelf()
	def reloadConfig(self, c):
		return self.worker.CommonBehavior_reloadConfig()
	def setParameterList(self, l, c):
		return self.worker.CommonBehavior_setParameterList(l)
	def setPeriod(self, period, c):
		return self.worker.CommonBehavior_setPeriod(period)
	def timeAwake(self, c):
		return self.worker.CommonBehavior_timeAwake()
