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

import time
import traceback
from datetime import datetime

import cv2
import imutils
import numpy as np
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QApplication

from games.genericDragGame.genericDragGame import GameScreen
from games.PaintGame.PaintGame import PaintGame
from genericworker import *
# from modules.AdminInterface import AdminInterface
from modules.CalibrationStateMachine import ManualCalibrationStateMachine
from modules.HandMouse import MultiHandMouses
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
		# self.login_widget = QLoginWidget()
		# self.login_widget.login_executed.connect(self.login_executed)
		# self.admin_interface = AdminInterface()
		# self.admin_interface.add_player_button.clicked.connect(self.add_new_player)
		# self.admin_interface.remove_player_button.clicked.connect(self.remove_player)
		# self.admin_interface.reset_game_button.clicked.connect(self.reset_game)
		# self.admin_interface.close_main_window.connect(self.quit_app)
		# self.admin_interface.admin_image.set_max_width(640)
		# self.admin_interface.show()
		self.hide()
		self.debug = True
		self.tv_image = QImageWidget()
		self.tv_image.mouse_pressed.connect(self.mouse_pressed_on_tv)
		self.tv_image.mouse_released.connect(self.mouse_released_on_tv)
		self.mouse_grab = False
		# Used to put the apriltag marks more and more inside the screen

		# Size of second screen
		rec = QApplication.desktop().screenGeometry(1)
		self.screen_1_width = rec.width() - 20
		self.screen_1_height = rec.height() - 20
		rec = QApplication.desktop().screenGeometry(0)
		self.screen_0_width = rec.width() - 20
		self.screen_0_height = rec.height() - 20
		self.calibrator = ManualCalibrationStateMachine(self.screen_1_width, self.screen_1_height)
		# TODO: would be the size of the second screen
		# self.screen_height = 740
		# self.screen_width = 1360
		self.screen_1_factor = 1
		self.tv_canvas = []
		if self.debug:
			self.tv_image.show_on_second_screen()
		self.Period = 20
		self.timer.start(self.Period)
		self.hand_track = []
		self.hand_mouses = MultiHandMouses()
		self._current_game_name = None
		# self._game = TakeDragGame()
		# self._game.show()
		self._available_games = {
			u"Lavar Ropa cerca":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/final_game1/final_game1.json"],
			u"Lavar Ropa lejos":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/clothclean/clothgame_near.json"],
			u"Painting":
				["PaintGame(self.screen_1_height, self.screen_1_width)", ""],
			u"Puzzle1":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game2.json"],
			u"Puzzle2":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game3.json"],
			u"Clothes":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game5.json"],
			u"Sorting":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game4.json"],
			u"Testing2":
				["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game4.json"]
			# u"Looser":
			# 	["GameScreen(self.screen_1_height, self.screen_1_width)", "resources/game6.json"]

		}
		self._game = None
		# self.admin_interface.games_combobox.currentIndexChanged.connect(self.update_game_selection)
		# self.update_game_selection()

		# self._admin_image = None
		self._mouse_release_point = None
		# TODO: Testing only. Remove
		self.add_new_player()

	def quit_app(self):
		self.current_state = "quitting"

	def update_game_selection(self, index=None):
		if self._current_game_name is not None:
			self._game = eval(unicode(self._available_games[unicode(self._current_game_name)][0]))
			self._game.game_frame.touch_signal.connect(self.detectedTouchPoints)
			self.current_state = "game_getting_player"
			self.reset_game()

	def reset_game(self):
		config_path = self._available_games[unicode(self.admin_interface.games_combobox.currentText())][1]
		self._game.init_game(config_path)

	def mouse_pressed_on_tv(self, point):
		self.mouse_grab = True
		print("Mouse pressed")

	def mouse_released_on_tv(self, point):
		self.mouse_grab = False
		self._mouse_release_point = point
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

		# testing = Status()
		# testing.currentStatus = StatusType.initializing
		# testing.date = datetime.now().strftime("%c")
		# self.gamemetrics_proxy.statusChanged(testing)

		start = time.time()
		if self.current_state == "starting":
			self.current_state = "waiting_login"
		# 	self.login_widget.setWindowTitle("Ingrese usuario")
		# 	self.login_widget.show()
		# elif self.current_state == "waiting_login":
		# 	self.admin_interface.statusBar().showMessage("Waiting login")
		# elif self.current_state == "calibrating":
		# 	self.tv_image.show_on_second_screen()
		# 	# self.calibration_image = cv2.resize(self.calibration_image, None,
		# 	# 									fx=(self.calibration_image.shape[0] / self.tv_image.height()),
		# 	# 									fy=(self.calibration_image.shape[1] / self.tv_image.width()),
		# 	# 									interpolation=cv2.INTER_CUBIC)
		# 	self.admin_interface.statusBar().showMessage(
		# 		"State: Calibrating. Calibrating state %d" % self.calibrator.state)
		# 	# TODO: Not working very well on the new big screen
		# 	# tags = self.getapriltags_proxy.checkMarcas()
		# 	# calibration_ended = self.calibrator.update(tags)
		#
		# 	####################### TO TEST
		# 	color, depth, points, _, _ = self.rgbd_proxy.getImage()
		# 	color, depth, _, _ = self.rgbd_proxy.getData()
		# 	frame = np.fromstring(color, dtype=np.uint8)
		# 	color_image = frame.reshape(480, 640, 3)
		# 	depth = np.ascontiguousarray(depth, dtype=np.uint8)
		# 	depth_gray_image = depth.reshape(480, 640)
		# 	color_image = cv2.flip(color_image, 0)
		# 	self._admin_image = color_image.copy()
		# 	self._admin_image = cv2.cvtColor(self._admin_image, cv2.COLOR_BGR2RGB)
		# 	calibration_ended = self.calibrator.update()
		# 	self._mouse_release_point = None
		# 	###################
		# 	if calibration_ended:
		# 		self.current_state = "game_getting_player"
		# 	# self._game2.set_frame(self.calibrator._screen_points)
		# 	self.tv_image.set_opencv_image(self.calibrator.image, False)
		# 	# if self.debug:
		# 	# 	self._admin_image = self.calibration_image.copy()
		# 	# 	cv2.imshow("DEBUG: tvGame: camera view", self._admin_image)
		# 	self.admin_interface.update_admin_image(self._admin_image)
		# 	cv2.waitKey(1)
		elif "game" in self.current_state:
			# try:
			# 	# image = self.camerasimple_proxy.getImage()
			# 	# frame = np.fromstring(image.image, dtype=np.uint8)
			# 	# frame = frame.reshape(image.width, image.height, image.depth)
			#
			# 	color, depth, _, _ = self.rgbd_proxy.getData()
			# 	frame = np.fromstring(color, dtype=np.uint8)
			# 	color_image = frame.reshape(480, 640, 3)
			# 	depth = np.array(depth, dtype=np.uint8)
			# 	depth_gray_image = depth.reshape(480, 640)
			# except Ice.Exception, e:
			# 	traceback.print_exc()
			# 	print (e)
			# 	return False
			# depth_gray_image = cv2.flip(depth_gray_image, 0)
			# color_image = cv2.flip(color_image, 0)
			# self._admin_image = color_image.copy()
			# self._admin_image = cv2.cvtColor(self._admin_image, cv2.COLOR_BGR2RGB)
			# # self._admin_image = imutils.resize(self._admin_image, width=640)
			# self.screen_1_factor = self.screen_1_height / float(color_image.shape[0])
			#
			# # self.tv_canvas = cv2.resize(self.tv_canvas, None, fx=self.screen_factor, fy=self.screen_factor,
			# # 						interpolation=cv2.INTER_CUBIC)
			if self.current_state == "game_getting_player":
				initialicing_status = Status()
				initialicing_status.currentStatus = StatusType.initializing
				initialicing_status.date = datetime.now().strftime("%c")
				self.gamemetrics_proxy.statusChanged(initialicing_status)
				self.tv_image.show_on_second_screen()
				if self.expected_hands is not None:
					if self.debug:
						print("Waiting to get %s players" % (self.expected_hands))
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
								# self._admin_image = self.draw_initial_masked_frame(color_image, search_roi)
								game_image = self.draw_initial_masked_frame(depth_rgb_image, search_roi)
								game_image = cv2.resize(game_image, None, fx=self.screen_1_factor,
														fy=self.screen_1_factor,
														interpolation=cv2.INTER_CUBIC)
								self.tv_image.set_opencv_image(game_image, False)
								self.expected_hands = self.handdetection_proxy.addNewHand(self.expected_hands,
																						  search_roi_class)
							except Ice.Exception, e:
								traceback.print_exc()
								print e

						elif current_hand_count >= self.expected_hands and self.expected_hands > 0:
							self.current_state = "game_tracking"
							self.reset_game()
							self._game.show()
							self.tv_image.hide()
					except Ice.Exception, e:
						traceback.print_exc()
						print e
				else:
					if self.debug:
						self.admin_interface.statusBar().showMessage("No player expected")
					image = self.tv_image.get_raw_image()
					image[:] = (255, 255, 255)
					# TODO: the size of the string would be substracted
					image = cv2.putText(image, "ADD NEW PLAYERS", (self.screen_1_width / 2, self.screen_1_height / 2),
										self.font, 1, [0, 0, 0], 2)
					self.tv_image.set_opencv_image(image, False)
			elif self.current_state == "game_tracking":
				try:
					self.hands = self.handdetection_proxy.getHands()
					if len(self.hands) < self.expected_hands:
						self.admin_interface.statusBar().showMessage("Hand Lost. recovering hand")
						self.current_state = "game_getting_player"
						self.hand_track = []
						self._game.hide()
						self.tv_image.show()
						return
					if self.debug:
						self.admin_interface.statusBar().showMessage("Debug: Traking %d hands" % (len(self.hands)))
					# TODO: It would be configurable from a file and dynamic
					self.paint_game()
				except Ice.Exception, e:
					traceback.print_exc()
					print e
			# if self.debug:
			self._admin_image = cv2.warpPerspective(self._admin_image, self.calibrator.homography,
													(self.screen_1_width, self.screen_1_height))
			# self.admin_interface.update_admin_image(self._admin_image)
			cv2.waitKey(1)
			# print "SpecificWorker.compute... in state %s with %d hands" % (self.current_state, len(self.hands))

			return True
		elif self.current_state == "quitting":
			exit(0)

	def paint_game(self):
		for hand in self.hands:
			if hand.detected or hand.tracked:
				if hand.centerMass2D:
					new_point = self.toHomogeneous(hand.centerMass2D)
					new_point = np.dot(self.calibrator.homography, new_point)
					new_point = self.fromHomogeneus(new_point)
					mouse = self.hand_mouses.add_state(hand.id, new_point, hand.detected)
					self._admin_image = self.draw_hand_full_overlay(self._admin_image, hand)
					if mouse.is_valid():
						self._game.update_pointer(mouse.hand_id(), mouse.last_pos()[0], mouse.last_pos()[1],
												  not mouse.last_state())

	def toHomogeneous(self, p):
		ret = np.resize(p, (len(p) + 1, 1))
		ret[-1][0] = 1.
		return ret

	def fromHomogeneus(self, p):
		return np.true_divide(p[:-1], p[-1])

	def login_executed(self, accepted):
		if accepted:
			self.current_state = "calibrating"
			self.tv_image.show_on_second_screen()
			self.login_widget.hide()

	def add_new_player(self, name=""):
		if self.expected_hands is None:
			self.expected_hands = 1
		else:
			self.expected_hands += 1
		# self.admin_interface.players_lcd.display(self.expected_hands)
		# self.admin_interface.remove_player_button.setEnabled(True)

	def remove_player(self):
		if self.expected_hands is not None:
			if self.expected_hands > 0:
				self.expected_hands -= 1
			else:
				self.expected_hands = 0
				# self.admin_interface.remove_player_button.setEnabled(False)
		# self.admin_interface.players_lcd.display(self.expected_hands)

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

	def draw_hand_full_overlay(self, frame, hand):
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

		if hand.centerMass2D is not None:
			# Draw center mass
			cv2.circle(frame, tuple(hand.centerMass2D), 7, [100, 0, 255], 2)
			cv2.putText(frame, 'Center', tuple(hand.centerMass2D), self.font, 0.5, (255, 255, 255), 1)

		hand_string = "hand %d %s: D=%s|T=%s|L=%s" % (
			hand.id, str(hand.centerMass2D), str(hand.detected), str(hand.tracked), str(hand.truthValue))
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
				p0 = self.hand_track[i - 1]
				cv2.line(frame, tuple(p0), tuple(p1), (0, 0, 255), 3)
		return frame


	#
	# adminReset
	#
	def adminReset(self):
		print("adminReset")
		# self.reset_game()

		pass


	#
	# adminContinue
	#
	def adminContinue(self):
		print("adminContinue")
		pass


	#
	# adminStop
	#
	def adminStop(self):
		print("adminStop")


	#
	# adminStart
	#
	def adminStart(self, players, game):
		print("adminStart", players, game)
		for player in players:
			self.add_new_player(player)
		self._current_game_name = game
		self.update_game_selection()




	#
	# adminPause
	#
	def adminPause(self):
		print("adminPause")

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
		#self.touchpoints_proxy.detectedTouchPoints(touch_points)
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

	def detectedTouchPoints(self, qt_touch_points):
		touch_points = []
		state_mapping = {Qt.TouchPointPressed: StateEnum.TouchPointPressed,
						 Qt.TouchPointMoved: StateEnum.TouchPointMoved,
						 Qt.TouchPointStationary: StateEnum.TouchPointPressed,
						 Qt.TouchPointReleased: StateEnum.TouchPointReleased}
		for qt_t_point in qt_touch_points:
			aux_point = qt_t_point.lastPos()
			tp = TouchPoint(id=qt_t_point.id(),
											state=state_mapping[qt_t_point.state()],
											fingertip=[qt_t_point.screenPos().x(), qt_t_point.screenPos().y()],
											lastPos=[aux_point.x(), aux_point.y()])
			touch_points.append(tp)
		print "TouchPoint Detected:"+str(tp)
		self.touchpoints_proxy.detectedTouchPoints(touch_points)
