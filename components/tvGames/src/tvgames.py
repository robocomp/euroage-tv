#!/usr/bin/env python
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

# \mainpage RoboComp::tvgames
#
# \section intro_sec Introduction
#
# Some information about the component...
#
# \section interface_sec Interface
#
# Descroption of the interface provided...
#
# \section install_sec Installation
#
# \subsection install1_ssec Software depencences
# Software dependences....
#
# \subsection install2_ssec Compile and install
# How to compile/install the component...
#
# \section guide_sec User guide
#
# \subsection config_ssec Configuration file
#
# <p>
# The configuration file...
# </p>
#
# \subsection execution_ssec Execution
#
# Just: "${PATH_TO_BINARY}/tvgames --Ice.Config=${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import sys, traceback, IceStorm, subprocess, threading, time, Queue, os, copy

# Ctrl+c handling
import signal

from PySide2 import QtCore
from PySide2 import QtWidgets

from specificworker import *


class CommonBehaviorI(RoboCompCommonBehavior.CommonBehavior):
	def __init__(self, _handler):
		self.handler = _handler
	def getFreq(self, current = None):
		self.handler.getFreq()
	def setFreq(self, freq, current = None):
		self.handler.setFreq()
	def timeAwake(self, current = None):
		try:
			return self.handler.timeAwake()
		except:
			print 'Problem getting timeAwake'
	def killYourSelf(self, current = None):
		self.handler.killYourSelf()
	def getAttrList(self, current = None):
		try:
			return self.handler.getAttrList()
		except:
			print 'Problem getting getAttrList'
			traceback.print_exc()
			status = 1
			return

#SIGNALS handler
def sigint_handler(*args):
	QtCore.QCoreApplication.quit()
    
if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	params = copy.deepcopy(sys.argv)
	if len(params) > 1:
		if not params[1].startswith('--Ice.Config='):
			params[1] = '--Ice.Config=' + params[1]
	elif len(params) == 1:
		params.append('--Ice.Config=config')
	ic = Ice.initialize(params)
	status = 0
	mprx = {}
	parameters = {}
	for i in ic.getProperties():
		parameters[str(i)] = str(ic.getProperties().getProperty(i))

	# Topic Manager
	proxy = ic.getProperties().getProperty("TopicManager.Proxy")
	obj = ic.stringToProxy(proxy)
	try:
		topicManager = IceStorm.TopicManagerPrx.checkedCast(obj)
	except Ice.ConnectionRefusedException, e:
		print 'Cannot connect to IceStorm! ('+proxy+')'
		status = 1

	# Remote object connection for CameraSimple
	try:
		proxyString = ic.getProperties().getProperty('CameraSimpleProxy')
		try:
			basePrx = ic.stringToProxy(proxyString)
			camerasimple_proxy = CameraSimplePrx.checkedCast(basePrx)
			mprx["CameraSimpleProxy"] = camerasimple_proxy
		except Ice.Exception:
			print 'Cannot connect to the remote object (CameraSimple)', proxyString
			#traceback.print_exc()
			status = 1
	except Ice.Exception, e:
		print e
		print 'Cannot get CameraSimpleProxy property.'
		status = 1


	# Remote object connection for GetAprilTags
	try:
		proxyString = ic.getProperties().getProperty('GetAprilTagsProxy')
		try:
			basePrx = ic.stringToProxy(proxyString)
			getapriltags_proxy = GetAprilTagsPrx.checkedCast(basePrx)
			mprx["GetAprilTagsProxy"] = getapriltags_proxy
		except Ice.Exception:
			print 'Cannot connect to the remote object (GetAprilTags)', proxyString
			#traceback.print_exc()
			status = 1
	except Ice.Exception, e:
		print e
		print 'Cannot get GetAprilTagsProxy property.'
		status = 1


	# Remote object connection for HandDetection
	try:
		proxyString = ic.getProperties().getProperty('HandDetectionProxy')
		try:
			basePrx = ic.stringToProxy(proxyString)
			handdetection_proxy = HandDetectionPrx.checkedCast(basePrx)
			mprx["HandDetectionProxy"] = handdetection_proxy
		except Ice.Exception:
			print 'Cannot connect to the remote object (HandDetection)', proxyString
			#traceback.print_exc()
			status = 1
	except Ice.Exception, e:
		print e
		print 'Cannot get HandDetectionProxy property.'
		status = 1


	# Remote object connection for RGBD
	try:
		proxyString = ic.getProperties().getProperty('RGBDProxy')
		try:
			basePrx = ic.stringToProxy(proxyString)
			rgbd_proxy = RGBDPrx.checkedCast(basePrx)
			mprx["RGBDProxy"] = rgbd_proxy
		except Ice.Exception:
			print 'Cannot connect to the remote object (RGBD)', proxyString
			#traceback.print_exc()
			status = 1
	except Ice.Exception, e:
		print e
		print 'Cannot get RGBDProxy property.'
		status = 1


	# Create a proxy to publish a GameMetrics topic
	topic = False
	try:
		topic = topicManager.retrieve("GameMetrics")
	except:
		pass
	while not topic:
		try:
			topic = topicManager.retrieve("GameMetrics")
		except IceStorm.NoSuchTopic:
			try:
				topic = topicManager.create("GameMetrics")
			except:
				print 'Another client created the GameMetrics topic? ...'
	pub = topic.getPublisher().ice_oneway()
	gamemetricsTopic = GameMetricsPrx.uncheckedCast(pub)
	mprx["GameMetricsPub"] = gamemetricsTopic


	# Create a proxy to publish a TouchPoints topic
	topic = False
	try:
		topic = topicManager.retrieve("TouchPoints")
	except:
		pass
	while not topic:
		try:
			topic = topicManager.retrieve("TouchPoints")
		except IceStorm.NoSuchTopic:
			try:
				topic = topicManager.create("TouchPoints")
			except:
				print 'Another client created the TouchPoints topic? ...'
	pub = topic.getPublisher().ice_oneway()
	touchpointsTopic = TouchPointsPrx.uncheckedCast(pub)
	mprx["TouchPointsPub"] = touchpointsTopic

	if status == 0:
		worker = SpecificWorker(mprx)
		worker.setParams(parameters)
	else:
		print "Error getting required connections, check config file"
		sys.exit(-1)

	adapter = ic.createObjectAdapter('AdminGame')
	adapter.add(AdminGameI(worker), ic.stringToIdentity('admingame'))
	adapter.activate()


	adapter = ic.createObjectAdapter('CommonBehavior')
	adapter.add(CommonBehaviorI(worker), ic.stringToIdentity('commonbehavior'))
	adapter.activate()


	adapter = ic.createObjectAdapter('TvGames')
	adapter.add(TvGamesI(worker), ic.stringToIdentity('tvgames'))
	adapter.activate()


	signal.signal(signal.SIGINT, sigint_handler)
	app.exec_()

	if ic:
		try:
			ic.destroy()
		except:
			traceback.print_exc()
			status = 1
