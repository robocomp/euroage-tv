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

import sys, os, Ice

ROBOCOMP = ''
try:
	ROBOCOMP = os.environ['ROBOCOMP']
except:
	print '$ROBOCOMP environment variable not set, using the default value /opt/robocomp'
	ROBOCOMP = '/opt/robocomp'
if len(ROBOCOMP)<1:
	print 'ROBOCOMP environment variable not set! Exiting.'
	sys.exit()

additionalPathStr = ''
icePaths = []
try:
	icePaths.append('/opt/robocomp/interfaces')
	SLICE_PATH = os.environ['SLICE_PATH'].split(':')
	for p in SLICE_PATH:
		icePaths.append(p)
		additionalPathStr += ' -I' + p + ' '
except:
	print 'SLICE_PATH environment variable was not exported. Using only the default paths'
	pass

ice_AdminGameInterface = False
for p in icePaths:
	print 'Trying', p, 'to load AdminGameInterface.ice'
	if os.path.isfile(p+'/AdminGameInterface.ice'):
		print 'Using', p, 'to load AdminGameInterface.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"AdminGameInterface.ice"
		Ice.loadSlice(wholeStr)
		ice_AdminGameInterface = True
		break
if not ice_AdminGameInterface:
	print 'Couldn\'t load AdminGameInterface'
	sys.exit(-1)
from EuroAgeGames import *
ice_CameraSimple = False
for p in icePaths:
	print 'Trying', p, 'to load CameraSimple.ice'
	if os.path.isfile(p+'/CameraSimple.ice'):
		print 'Using', p, 'to load CameraSimple.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"CameraSimple.ice"
		Ice.loadSlice(wholeStr)
		ice_CameraSimple = True
		break
if not ice_CameraSimple:
	print 'Couldn\'t load CameraSimple'
	sys.exit(-1)
from RoboCompCameraSimple import *
ice_CommonBehavior = False
for p in icePaths:
	print 'Trying', p, 'to load CommonBehavior.ice'
	if os.path.isfile(p+'/CommonBehavior.ice'):
		print 'Using', p, 'to load CommonBehavior.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"CommonBehavior.ice"
		Ice.loadSlice(wholeStr)
		ice_CommonBehavior = True
		break
if not ice_CommonBehavior:
	print 'Couldn\'t load CommonBehavior'
	sys.exit(-1)
from RoboCompCommonBehavior import *
ice_GetAprilTags = False
for p in icePaths:
	print 'Trying', p, 'to load GetAprilTags.ice'
	if os.path.isfile(p+'/GetAprilTags.ice'):
		print 'Using', p, 'to load GetAprilTags.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"GetAprilTags.ice"
		Ice.loadSlice(wholeStr)
		ice_GetAprilTags = True
		break
if not ice_GetAprilTags:
	print 'Couldn\'t load GetAprilTags'
	sys.exit(-1)
from RoboCompGetAprilTags import *
ice_HandDetection = False
for p in icePaths:
	print 'Trying', p, 'to load HandDetection.ice'
	if os.path.isfile(p+'/HandDetection.ice'):
		print 'Using', p, 'to load HandDetection.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"HandDetection.ice"
		Ice.loadSlice(wholeStr)
		ice_HandDetection = True
		break
if not ice_HandDetection:
	print 'Couldn\'t load HandDetection'
	sys.exit(-1)
from RoboCompHandDetection import *
ice_RGBD = False
for p in icePaths:
	print 'Trying', p, 'to load RGBD.ice'
	if os.path.isfile(p+'/RGBD.ice'):
		print 'Using', p, 'to load RGBD.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"RGBD.ice"
		Ice.loadSlice(wholeStr)
		ice_RGBD = True
		break
if not ice_RGBD:
	print 'Couldn\'t load RGBD'
	sys.exit(-1)
from RoboCompRGBD import *
ice_TouchPoints = False
for p in icePaths:
	print 'Trying', p, 'to load TouchPoints.ice'
	if os.path.isfile(p+'/TouchPoints.ice'):
		print 'Using', p, 'to load TouchPoints.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"TouchPoints.ice"
		Ice.loadSlice(wholeStr)
		ice_TouchPoints = True
		break
if not ice_TouchPoints:
	print 'Couldn\'t load TouchPoints'
	sys.exit(-1)
from RoboCompTouchPoints import *
ice_TvGames = False
for p in icePaths:
	print 'Trying', p, 'to load TvGames.ice'
	if os.path.isfile(p+'/TvGames.ice'):
		print 'Using', p, 'to load TvGames.ice'
		preStr = "-I/opt/robocomp/interfaces/ -I"+ROBOCOMP+"/interfaces/ " + additionalPathStr + " --all "+p+'/'
		wholeStr = preStr+"TvGames.ice"
		Ice.loadSlice(wholeStr)
		ice_TvGames = True
		break
if not ice_TvGames:
	print 'Couldn\'t load TvGames'
	sys.exit(-1)
from RoboCompTvGames import *

class AdminGameI(AdminGame):
	def __init__(self, worker):
		self.worker = worker

	def adminReset(self, c):
		return self.worker.adminReset()
	def adminContinue(self, c):
		return self.worker.adminContinue()
	def adminStop(self, c):
		return self.worker.adminStop()
	def adminStart(self, players, game, c):
		return self.worker.adminStart(players, game)
	def adminPause(self, c):
		return self.worker.adminPause()