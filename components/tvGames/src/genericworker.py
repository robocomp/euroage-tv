#
# Copyright (C) 2018 by YOUR NAME HERE
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
from PySide import QtGui, QtCore

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


from commonbehaviorI import *
from tvgamesI import *

try:
	from ui_mainUI import *
except:
	print "Can't import UI file. Did you run 'make'?"
	sys.exit(-1)


class GenericWorker(QtGui.QWidget):
	kill = QtCore.Signal()


	def __init__(self, mprx):
		super(GenericWorker, self).__init__()


		self.rgbd_proxy = mprx["RGBDProxy"]
		self.camerasimple_proxy = mprx["CameraSimpleProxy"]
		self.handdetection_proxy = mprx["HandDetectionProxy"]
		self.getapriltags_proxy = mprx["GetAprilTagsProxy"]
		self.touchpoints_proxy = mprx["TouchPointsPub"]
		self.ui = Ui_guiDlg()
		self.ui.setupUi(self)
		self.show()


		self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
		self.Period = 30
		self.timer = QtCore.QTimer(self)


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
