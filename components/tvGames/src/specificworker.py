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
#

import time
import traceback

import cv2
import numpy as np
from PyQt4.QtGui import QApplication

from genericworker import *
from modules.AdminInterface import AdminInterface
from modules.QImageWidget import QImageWidget
from modules.QtLogin import QLoginWidget


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.expected_hands = None
		self.hands = []
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.current_state = "calibrating"
		self.login_widget = QLoginWidget()
		self.login_widget.login_executed.connect(self.login_executed)
		self.admin_interface = AdminInterface()
		self.admin_interface.add_player_button.clicked.connect(self.add_new_player)
		self.admin_interface.remove_player_button.clicked.connect(self.remove_player)
		self.admin_interface.show()
		self.hide()
		self.debug = True
		self.tv_image = QImageWidget()
		self.tv_image.mouse_pressed.connect(self.mouse_pressed_on_tv)
		self.tv_image.mouse_released.connect(self.mouse_released_on_tv)
		self.calibration_state = 0
		self.calibration_image = []
		self.origPts = []
		self.refPts = []
		self.mouse_grab = False
		# Used to put the apriltag marks more and more inside the screen
		self.tv_reduction = 0
		self.april_0 = cv2.imread('resources/april_0.png')
		self.april_0 = cv2.resize(self.april_0, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
		self.april_1 = cv2.imread('resources/april_1.png')
		self.april_1 = cv2.resize(self.april_1, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
		self.april_2 = cv2.imread('resources/april_2.png')
		self.april_2 = cv2.resize(self.april_2, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
		self.april_3 = cv2.imread('resources/april_3.png')
		self.april_3 = cv2.resize(self.april_3, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
		# Size of second screen
		rec = QApplication.desktop().screenGeometry(1)
		self.screen_width = rec.width() - 20
		self.screen_height = rec.height() - 20
		# TODO: would be the size of the second screen
		# self.screen_height = 740
		# self.screen_width = 1360
		self.screen_factor = 1

		self.calibration_image = np.array(np.zeros((self.screen_height, self.screen_width, 3)), dtype=np.uint8)
		self.calibration_image[:] = (255, 255, 255)
		if self.debug:
			self.tv_image.show_on_second_screen()
		self.Period = 20
		self.timer.start(self.Period)
		self.hand_track = []

	def mouse_pressed_on_tv(self):
		self.mouse_grab = True
		print("Mouse pressed")

	def mouse_released_on_tv(self):
		self.mouse_grab = False
		print("Mouse released")

	def setParams(self, params):
		# try:
		#	self.innermodel = InnerModel(params["InnerModelPath"])
		# except:
		#	traceback.print_exc()
		#	self.admin_interface.statusBar().showMessage("Error reading config params")
		return True

	@QtCore.Slot()
	def compute(self):
		start = time.time()
		if self.current_state == "starting":
			self.current_state = "waiting_login"
			self.login_widget.setWindowTitle("Ingrese usuario")
			self.login_widget.show()
		elif self.current_state == "waiting_login":
			self.admin_interface.statusBar().showMessage("Waiting login")
		elif self.current_state == "calibrating":
			self.tv_image.show_on_second_screen()
			# self.calibration_image = cv2.resize(self.calibration_image, None,
			# 									fx=(self.calibration_image.shape[0] / self.tv_image.height()),
			# 									fy=(self.calibration_image.shape[1] / self.tv_image.width()),
			# 									interpolation=cv2.INTER_CUBIC)
			self.admin_interface.statusBar().showMessage("State: calibrating")
			self.admin_interface.statusBar().showMessage("Calibrating state %d" % (self.calibration_state))
			tags = self.getapriltags_proxy.checkMarcas()

			self.calibrate(tags)
			if self.calibration_state == 4:
				self.current_state = "game_getting_player"
			self.tv_image.set_opencv_image(self.calibration_image, False)
			# if self.debug:
			# 	admin_image = self.calibration_image.copy()
			# 	cv2.imshow("DEBUG: tvGame: camera view", admin_image)
			cv2.waitKey(1)
		elif "game" in self.current_state:
			try:
				# image = self.camerasimple_proxy.getImage()
				# frame = np.fromstring(image.image, dtype=np.uint8)
				# frame = frame.reshape(image.width, image.height, image.depth)

				color, depth, _, _ = self.rgbd_proxy.getData()
				frame = np.fromstring(color, dtype=np.uint8)
				color_image = frame.reshape(480, 640, 3)
				depth = np.array(depth, dtype=np.uint8)
				depth_gray_image = depth.reshape(480, 640)
			except Ice.Exception, e:
				traceback.print_exc()
				print e
				return False
			depth_gray_image = cv2.flip(depth_gray_image, 0)
			color_image = cv2.flip(color_image, 0)
			admin_image = color_image.copy()
			admin_image = cv2.warpPerspective(admin_image, self.homography, (self.screen_width, self.screen_height))
			if self.current_state == "game_getting_player":
				self.tv_image.show_on_second_screen()
				if self.expected_hands is not None:
					if self.debug:
						self.admin_interface.statusBar().showMessage(
							"Waiting to get %s players" % (self.expected_hands))
					try:
						current_hand_count = self.handdetection_proxy.getHandsCount()

						if current_hand_count < self.expected_hands:
							try:
								search_roi_class = TRoi()
								search_roi_class.y = 480 / 2 - 100
								search_roi_class.x = 640 / 2 - 100
								search_roi_class.w = 200
								search_roi_class.h = 200
								search_roi = (
									search_roi_class.x, search_roi_class.y, search_roi_class.h, search_roi_class.w)

								depth_rgb_image = cv2.cvtColor(depth_gray_image, cv2.COLOR_GRAY2BGR)
								# admin_image = self.draw_initial_masked_frame(color_image, search_roi)
								game_image = self.draw_initial_masked_frame(depth_rgb_image, search_roi)
								self.screen_factor = self.screen_height / float(game_image.shape[0])
								game_image = cv2.resize(game_image, None, fx=self.screen_factor, fy=self.screen_factor,
														interpolation=cv2.INTER_CUBIC)
								self.tv_image.set_opencv_image(game_image, False)
								self.expected_hands = self.handdetection_proxy.addNewHand(self.expected_hands,
																						  search_roi_class)
							except Ice.Exception, e:
								traceback.print_exc()
								print e

						elif current_hand_count >= self.expected_hands and self.expected_hands > 0:
							self.current_state = "game_tracking"
					except Ice.Exception, e:
						traceback.print_exc()
						print e
				else:
					if self.debug:
						self.admin_interface.statusBar().showMessage("No player expected")
					image = self.tv_image.get_raw_image()
					image[:] = (255, 255, 255)
					# TODO: the size of the string would be substracted
					image = cv2.putText(image, "ADD NEW PLAYERS", (self.screen_width / 2, self.screen_height / 2),
										self.font, 1, [0, 0, 0], 2)
					self.tv_image.set_opencv_image(image, False)
			elif self.current_state == "game_tracking":

				try:
					self.hands = self.handdetection_proxy.getHands()
					if len(self.hands) < self.expected_hands:
						self.admin_interface.statusBar().showMessage("Hand Lost recovering hand")
						self.current_state = "game_getting_player"
						self.hand_track = []
					if self.debug:
						self.admin_interface.statusBar().showMessage("Debug: Traking %d hands" % (len(self.hands)))
					tv_image = np.zeros(color_image.shape, dtype="uint8")
					tv_image[::] = 255
					for hand in self.hands:
						if hand.centerMass:
							new_point = self.toHomogeneous(hand.centerMass)
							new_point = np.dot(self.homography, new_point)
							if self.mouse_grab:
								# sould be done for each hand
								self.hand_track.append(hand.centerMass)
						admin_image = self.draw_hand_overlay(admin_image, hand)
						# tv_image = self.draw_hand_overlay(tv_image, hand)
						# Not working currently
						# tv_image = self.draw_pointer(tv_image, new_point[:2])
						# zero_point = self.toHomogeneous([0,0])
						# zero_point = np.dot(self.homography, zero_point)
						# tv_image = self.draw_pointer(tv_image, zero_point[:2])

						tv_image = self.draw_hand_track(tv_image)
					if self.screen_factor != 1:
						tv_image = cv2.resize(tv_image, None, fx=self.screen_factor, fy=self.screen_factor,
											  interpolation=cv2.INTER_CUBIC)
					self.tv_image.set_opencv_image(tv_image, False)
				except Ice.Exception, e:
					traceback.print_exc()
					print e
			# if self.debug:
			self.admin_interface.update_admin_image(admin_image)
			cv2.waitKey(1)
			# print "SpecificWorker.compute... in state %s with %d hands" % (self.current_state, len(self.hands))

			return True

	def toHomogeneous(self, p):
		ret = np.resize(p, (len(p) + 1, 1))
		ret[-1][0] = 1.
		return ret

	def calibrate(self, tags):
		if self.calibration_state > 4 or self.calibration_state < 0:
			return
		detections = tags
		if self.calibration_state == 0:
			self.calibration_image[:] = (255, 255, 255)
			try:
				self.calibration_image = self.copyRoi(self.calibration_image, self.april_0, self.tv_reduction,
													  self.tv_reduction)
			except:
				print("Calibration failed")
				self.calibration_state = -1
			if len(detections) == 1:
				if detections[0].id == 0:
					self.origPts.append([5, 5])
					self.refPts.append([detections[0].tx - 2,
										detections[0].ty - 2])
					self.calibration_state = 1
					self.calibration_image[:] = (255, 255, 255)
					cv2.waitKey(1000)
					self.tv_reduction = 0
			else:
				self.tv_reduction += 1
		elif self.calibration_state == 1:
			self.calibration_image[:] = (255, 255, 255)
			self.copyRoi(self.calibration_image, self.april_1,
						 self.screen_height - self.april_1.shape[0] - self.tv_reduction, self.tv_reduction)
			if len(detections) == 1:
				if detections[0].id == 1:
					self.origPts.append([5, self.screen_width])
					self.refPts.append([detections[0].tx - 2,
										detections[0].ty + 2])
					self.calibration_state = 2
					self.calibration_image[:] = (255, 255, 255)
					cv2.waitKey(1000)
					self.tv_reduction = 0
			else:
				self.tv_reduction += 1
		elif self.calibration_state == 2:
			self.calibration_image[:] = (255, 255, 255)
			self.copyRoi(self.calibration_image, self.april_2, self.tv_reduction,
						 self.screen_width - self.april_2.shape[1] - self.tv_reduction)
			if len(detections) == 1:
				if detections[0].id == 2:
					self.origPts.append([self.screen_width, 5])
					self.refPts.append([detections[0].tx + 2,
										detections[0].ty - 2])
					self.calibration_state = 3
					self.calibration_image[:] = (255, 255, 255)
					cv2.waitKey(1000)
					self.tv_reduction = 0
			else:
				self.tv_reduction += 1
		elif self.calibration_state == 3:
			self.calibration_image[:] = (255, 255, 255)
			self.copyRoi(self.calibration_image, self.april_3,
						 self.screen_height - self.april_3.shape[0] - self.tv_reduction,
						 self.screen_width - self.april_3.shape[1] - self.tv_reduction)
			if len(detections) == 1:
				if detections[0].id == 3:
					self.origPts.append([self.screen_width, self.screen_height])
					self.refPts.append([detections[0].tx + 2,
										detections[0].ty + 2])
					self.calibration_state = 4
					self.calibration_image[:] = (255, 255, 255)
					self.homography, _ = cv2.findHomography(np.array(self.refPts), np.array(self.origPts))
					self.admin_interface.statusBar().showMessage("Calibration ended")
			else:
				self.tv_reduction += 1

	def copyRoi(self, bigImage, small, row, col):
		# initial number of rows and columns
		rows = small.shape[0]
		cols = small.shape[1]
		bigImage[row:row + rows, col:col + cols, :] = small[:rows, :cols, :]
		return bigImage

	def login_executed(self, accepted):
		if accepted:
			self.current_state = "calibrating"
			self.tv_image.show_on_second_screen()
			self.login_widget.hide()

	def add_new_player(self):
		if self.expected_hands is None:
			self.expected_hands = 1
		else:
			self.expected_hands += 1
		self.admin_interface.players_lcd.display(self.expected_hands)
		self.admin_interface.remove_player_button.setEnabled(True)

	def remove_player(self):
		if self.expected_hands is not None:
			if self.expected_hands > 0:
				self.expected_hands -= 1
			else:
				self.expected_hands = 0
				self.admin_interface.remove_player_button.setEnabled(False)
		self.admin_interface.players_lcd.display(self.expected_hands)

	#### FOR TESTING PORPOSE ONLY

	#### FOR TESTING PORPOSE ONLY

	def draw_initial_masked_frame(self, frame, search_roi):
		masked_frame = np.zeros(frame.shape, dtype="uint8")
		masked_frame[::] = 255
		template_x, template_y, template_w, template_h = search_roi
		cv2.putText(masked_frame, "PLEASE PUT YOUR HAND HERE", (template_x - 100, template_y + template_h + 10),
					self.font, 1, [0, 0, 0], 2)

		masked_frame = cv2.rectangle(masked_frame, (template_x, template_y),
									 (template_x + template_w, template_y + template_h), [0, 0, 0])
		alpha = 0.7
		beta = (1.0 - alpha)
		masked_frame = cv2.addWeighted(frame, alpha, masked_frame, beta, 0.0)
		return masked_frame

	def draw_hand_overlay(self, frame, hand):
		if hand.detected:
			for finger_number, fingertip in enumerate(hand.fingertips):
				cv2.circle(frame, tuple(fingertip), 10, [255, 100, 255], 3)
				cv2.putText(frame, 'finger' + str(finger_number), tuple(fingertip), self.font, 0.5,
							(255, 255, 255),
							1)
			for defect in hand.intertips:
				cv2.circle(frame, tuple(defect), 8, [211, 84, 0], -1)
		# self.draw_contour_features(frame, hand.contour)
		# x, y, w, h = hand.bounding_rect
		# cv2.putText(frame, (str(w)), (x + w, y), self.font, 0.3, [255, 255, 255], 1)
		# cv2.putText(frame, (str(h)), (x + w, y + h), self.font, 0.3, [255, 255, 255], 1)
		# cv2.putText(frame, (str(w * h)), (x + w / 2, y + h / 2), self.font, 0.3, [255, 255, 255], 1)
		# cv2.putText(frame, (str(x)+", "+str(y)), (x-10, y-10), self.font, 0.3, [255, 255, 255], 1)
		# cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

		if hand.detected or hand.tracked:
			cv2.drawContours(frame, [np.array(hand.contour, dtype=int)], -1, (0, 0, 0), 2)

		points = np.array(hand.positions)
		cv2.polylines(img=frame, pts=np.int32([points]), isClosed=False, color=(255, 0, 200))
		tail_length = 15
		if len(points) > tail_length:
			for i in np.arange(1, tail_length):
				ci = len(points) - tail_length + i
				thickness = int((float(i) / tail_length) * 13) + 1
				cv2.line(frame, tuple(points[ci - 1]), tuple(points[ci]), (0, 0, 255), thickness)

		if hand.centerMass is not None:
			# Draw center mass
			cv2.circle(frame, tuple(hand.centerMass), 7, [100, 0, 255], 2)
			cv2.putText(frame, 'Center', tuple(hand.centerMass), self.font, 0.5, (255, 255, 255), 1)

		hand_string = "hand %d %s: D=%s|T=%s|L=%s" % (
			hand.id, str(hand.centerMass), str(hand.detected), str(hand.tracked), str(hand.truthValue))
		cv2.putText(frame, hand_string, (10, 30 + 15 * int(hand.id)), self.font, 0.5, (255, 255, 255), 1)
		return frame

	def draw_pointer(self, frame, point, color=[100, 0, 255]):
		if point is not None:
			# Draw center mass
			cv2.circle(frame, tuple(point), 7, color, 2)
		# cv2.putText(frame, 'Center', tuple(point), self.font, 0.5, (255, 255, 255), 1)
		return frame

	def draw_hand_track(self, frame):
		if len(self.hand_track) > 2:
			for i in np.arange(1, len(self.hand_track)):
				p1 = self.hand_track[i]
				p0 = self.hand_track[i-1]
				cv2.line(frame, tuple(p0), tuple(p1), (0, 0, 255), 3)
		return frame

	#
	# reloadConfig
	#
	def reloadConfig(self):
		#
		# implementCODE
		#
		pass

	#
	# setPeriod
	#
	def setPeriod(self, period):
		#
		# implementCODE
		#
		pass

	#
	# getState
	#
	def getState(self):
		ret = State()
		#
		# implementCODE
		#
		return ret

	#
	# setParameterList
	#
	def setParameterList(self, l):
		#
		# implementCODE
		#
		pass

	#
	# timeAwake
	#
	def timeAwake(self):
		ret = int()
		#
		# implementCODE
		#
		return ret

	#
	# getParameterList
	#
	def getParameterList(self):
		ret = ParameterList()
		#
		# implementCODE
		#
		return ret

	#
	# killYourSelf
	#
	def killYourSelf(self):
		#
		# implementCODE
		#
		pass

	#
	# getPeriod
	#
	def getPeriod(self):
		ret = int()
		#
		# implementCODE
		#
		return ret

	#
	# launchGame
	#
	def launchGame(self, name):
		#
		# implementCODE
		#
		pass
