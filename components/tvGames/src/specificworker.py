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
import json
import time
import traceback
from datetime import datetime

import cv2
import imutils
import numpy as np
from PySide2.QtCore import Slot, Qt, QTimer
from PySide2.QtWidgets import QApplication

from games.genericDragGame.genericDragGame import GameScreen, TakeDragGame
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

FILE_PATH = os.path.dirname(__file__)


class Player:
	def __init__(self, id=-1, name=""):
		self.id = id
		self.name = name
		self.tracked = False

#      struct Position
#      {
#         float x;
#         float y;
#      };
#
#     struct Metrics
#     {
#         string	currentDate;
#         Position pos;
#         bool	screenTouched;
#         bool	handClosed;
#         int	numHelps;
#         int	numChecked;
#         int	numHits;
#         int	numFails;
#
#     };
class GameMetrics(Metrics):
	def __init__(self):
		super(GameMetrics, self).__init__()
		self.currentDate = datetime.now().isoformat()
		self.numHelps = 0
		self.numChecked = 0
		self.numHits = 0
		self.numFails = 0
		self.handClosed = False
		self.screenTouched = False
		self.pos = Position()

	def increment_helps(self, quantity=1):
		self.numHelps+=quantity

	def increment_checked(self, quantity=1):
		self.numChecked+=quantity

	def increment_hits(self, quantity=1):
		self.numHits+=quantity

	def increment_fails(self, quantity=1):
		self.numFails+=quantity

	def set_screen_touched(self, touched=True, pos=None):
		self.screenTouched = touched
		if pos:
			self.pos.x = pos.x
			self.pos.y = pos.y

	def set_hand_closed(self, closed=True, pos=None):
		self.handClosed = closed
		if pos:
			self.pos.x = pos.x
			self.pos.y = pos.y





class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self._current_players = []
		self.hands = []
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self._current_state = "calibrating"
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

		self.mouse_grab = False
		# Used to put the apriltag marks more and more inside the screen

		# Size of second screen
		rec = QApplication.desktop().screenGeometry(1)
		screen_1_width = rec.width() - 20
		screen_1_height = rec.height() - 20
		rec = QApplication.desktop().screenGeometry(0)
		screen_0_width = rec.width() - 20
		screen_0_height = rec.height() - 20
		if screen_1_width <0 or screen_1_height<0:
			self._game_screen_width = screen_0_width
			self._game_screen_height = screen_0_height
		else:
			self._game_screen_width = screen_1_width
			self._game_screen_height = screen_1_height
		self.calibrator = ManualCalibrationStateMachine(self._game_screen_width, self._game_screen_height)




		# TODO: would be the size of the second screen
		# self.screen_height = 740
		# self.screen_width = 1360
		self.screen_factor = min([self._game_screen_width / 640., self._game_screen_height / 480.])
		self.tv_canvas = []
		if self.debug:
			# self.tv_image.show_on_second_screen()
			pass
		self.Period = 20
		self.timer.start(self.Period)
		self._player_to_hand_index = {}
		self.hand_track = []
		self.hand_mouses = MultiHandMouses()
		self._current_game_name = None

		# game name and path
		self._available_games = {}
		self._game = None

		# self._admin_image = None
		self._mouse_release_point = None

		self._game_metrics = GameMetrics()

		# TODO: Testing only. Remove
		# self.adminStartSession("Juan Lopez")

		self.tv_image.show_on_second_screen()

		self.game_machine.start()

	def __del__(self):
		print 'SpecificWorker destructor'

	def quit_app(self):
		self._current_state = "quitting"

	def update_game_selection(self, index=None):
		if self._current_game_name is not None:
			self._game = GameScreen(self._game_screen_width, self._game_screen_height)
			self._game.game_frame.touch_signal.connect(self.detectedTouchPoints)
			self._game.help_clicked.connect(self.game_help_clicked)
			self._game.check_clicked.connect(self.game_check_clicked)
			self._game.score_update.connect(self.game_score_update)
			self.reset_game()


	def game_help_clicked(self):
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numHelps += 1
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)

	def game_check_clicked(self):
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numChecked += 1
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)

	def game_score_update(self, win, fail):
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numFails = fail
		self._game_metrics.numHits = win
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)


	def reset_game(self):
		config_path = self._available_games[unicode(self._current_game_name)]
		self._game.init_game(config_path)

	def mouse_pressed_on_tv(self, point):
		self.mouse_grab = True
		print("Mouse pressed")

	def mouse_released_on_tv(self, point):
		self.mouse_grab = False
		self._mouse_release_point = point
		print("Mouse released")

	def setParams(self, params):
		if "games_path" in params:
			self.load_available_games(params["games_path"])




		# try:
		#	self.innermodel = InnerModel(params["InnerModelPath"])
		# except:
		#	traceback.print_exc()
		#	self.admin_interface.statusBar().showMessage("Error reading config params")
		return True


# =============== Slots methods for State Machine ===================
# ===================================================================
	#
	# sm_session_start_wait
	#
	@QtCore.Slot()
	def sm_session_start_wait(self):
		print("Entered state session_start_wait")

		# TODO: Test only. Remove on production
		# self.session_start_waittosession_init.emit()
		self.send_status_change(StatusType.waitingSession)


	#
	# sm_game_end
	#
	@QtCore.Slot()
	def sm_game_end(self):
		print("Entered state game_end")
		won = self._game.end_game()
		if won:
			self.game_endtogame_won.emit()
		else:
			self.game_endtogame_lost.emit()



	#
	# sm_game_init
	#
	@QtCore.Slot()
	def sm_game_init(self):
		print("Entered state game_init")

		# TODO: Test only. Remove on production
		self._current_game_name = "Prepara la tortilla"

		self._game = None
		self.update_game_selection()
		self._game.show()
		self.game_inittogame_loop.emit()

	#
	# sm_game_loop
	#
	@QtCore.Slot()
	def sm_game_loop(self):
		self._game_metrics.currentDate = datetime.now().isoformat()
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)
		print("Entered state game_loop")
		self.send_status_change(StatusType.playingGame)
		QTimer.singleShot(200, self.game_looptogame_loop)

	#
	# sm_game_lost
	#
	@QtCore.Slot()
	def sm_game_lost(self):
		print("Entered state game_lost")
		self.send_status_change(StatusType.lostGame)
		QTimer.singleShot(3000, self.game_losttogame_start_wait)



	#
	# sm_game_pause
	#
	@QtCore.Slot()
	def sm_game_pause(self):
		print("Entered state game_pause")
		self._game.pause_game()
		self.send_status_change(StatusType.pausedGame)


	#
	# sm_game_reset
	#
	@QtCore.Slot()
	def sm_game_reset(self):
		print("Entered state game_reset")
		self._game.hide()
		self.game_resettogame_start_wait.emit()
		pass

	#
	# sm_game_resume
	#
	@QtCore.Slot()
	def sm_game_resume(self):
		print("Entered state game_resume")
		self._game.resume_game()
		self.game_resumetogame_loop.emit()

	#
	# sm_game_start_wait
	#
	@QtCore.Slot()
	def sm_game_start_wait(self):
		print("Entered state game_start_wait")

		# TODO: Test only. Remove on production
		# self.game_start_waittogame_init.emit()
		self.send_status_change(StatusType.waitingGame)
		QTimer.singleShot(200, self.game_start_waittogame_start_wait)



	#
	# sm_game_won
	#
	@QtCore.Slot()
	def sm_game_won(self):
		print("Entered state game_won")
		self.send_status_change(StatusType.wonGame)
		QTimer.singleShot(3000, self.game_losttogame_start_wait)


	#
	# sm_session_init
	#
	@QtCore.Slot()
	def sm_session_init(self):
		print("Entered state session_init")
		self.send_status_change(StatusType.initializingSession)

	

	#
	# sm_session_end
	#
	@QtCore.Slot()
	def sm_session_end(self):
		print("Entered state session_end")
		self.send_status_change(StatusType.endSession)
		self._game.pause_game()
		self._game.hide()
		self._game = None

	#
	# sm_player_acquisition_init
	#
	@QtCore.Slot()
	def sm_player_acquisition_init(self):
		print("Entered state player_acquisition_init")
		self.player_acquisition_inittoplayer_acquisition_loop.emit()
		self.send_status_change(StatusType.initializingSession)

	#
	# sm_player_acquisition_loop
	#
	@QtCore.Slot()
	def sm_player_acquisition_loop(self):
		print("Entered state player_acquisition_loop")
		acquired = True
		for player in self._current_players:
			if player.tracked is False:
				acquired = False
				self.obtain_player_id(player)
		#TODO: testing only. Remove on production
		acquired=True

		if acquired:
			self.player_acquisition_looptoplayer_acquisition_ended.emit()
		else:
			QTimer.singleShot(1000 / 33, self.player_acquisition_looptoplayer_acquisition_loop)

	#
	# sm_player_acquisition_ended
	#
	@QtCore.Slot()
	def sm_player_acquisition_ended(self):
		print("Entered state player_acquisition_ended")

		self.send_status_change(StatusType.readySession)
		# TODO: Testing only. remove on production
		self.session_inittogame_start_wait.emit()


# =================================================================
# =================================================================



	def load_available_games(self, path):
		self._available_games = {}
		full_path = os.path.join(FILE_PATH, path)
		# r=root, d=directories, f = files
		for root, dirs, files in os.walk(full_path):
			for file in files:
				if file.endswith(".json"):
					full_file_path = os.path.join(full_path, file)
					with open(full_file_path) as file_path:
						game_config = json.load(file_path)
						if "title" in game_config:
							self._available_games[game_config["title"]] = full_file_path


	# TODO: DEPRECATED. Moved to state machine logic. Check and remove.
	# @QtCore.Slot()
	# def compute(self):
	#
	# 	testing = Status()
	# 	testing.currentStatus = StatusType.initializing
	# 	testing.date = datetime.now().strftime("%c")
	# 	self.gamemetrics_proxy.statusChanged(testing)
	# 	print("Sending metrics")
	#
	# 	start = time.time()
	# 	if self._current_state == "starting":
	# 		self._current_state = "waiting_login"
	# 	# 	self.login_widget.setWindowTitle("Ingrese usuario")
	# 	# 	self.login_widget.show()
	# 	# elif self.current_state == "waiting_login":
	# 	# 	self.admin_interface.statusBar().showMessage("Waiting login")
	# 	# elif self.current_state == "calibrating":
	# 	# 	self.tv_image.show_on_second_screen()
	# 	# 	# self.calibration_image = cv2.resize(self.calibration_image, None,
	# 	# 	# 									fx=(self.calibration_image.shape[0] / self.tv_image.height()),
	# 	# 	# 									fy=(self.calibration_image.shape[1] / self.tv_image.width()),
	# 	# 	# 									interpolation=cv2.INTER_CUBIC)
	# 	# 	self.admin_interface.statusBar().showMessage(
	# 	# 		"State: Calibrating. Calibrating state %d" % self.calibrator.state)
	# 	# 	# TODO: Not working very well on the new big screen
	# 	# 	# tags = self.getapriltags_proxy.checkMarcas()
	# 	# 	# calibration_ended = self.calibrator.update(tags)
	# 	#
	# 	# 	####################### TO TEST
	# 	# 	color, depth, points, _, _ = self.rgbd_proxy.getImage()
	# 	# 	color, depth, _, _ = self.rgbd_proxy.getData()
	# 	# 	frame = np.fromstring(color, dtype=np.uint8)
	# 	# 	color_image = frame.reshape(480, 640, 3)
	# 	# 	depth = np.ascontiguousarray(depth, dtype=np.uint8)
	# 	# 	depth_gray_image = depth.reshape(480, 640)
	# 	# 	color_image = cv2.flip(color_image, 0)
	# 	# 	self._admin_image = color_image.copy()
	# 	# 	self._admin_image = cv2.cvtColor(self._admin_image, cv2.COLOR_BGR2RGB)
	# 	# 	calibration_ended = self.calibrator.update()
	# 	# 	self._mouse_release_point = None
	# 	# 	###################
	# 	# 	if calibration_ended:
	# 	# 		self.current_state = "game_getting_player"
	# 	# 	# self._game2.set_frame(self.calibrator._screen_points)
	# 	# 	self.tv_image.set_opencv_image(self.calibrator.image, False)
	# 	# 	# if self.debug:
	# 	# 	# 	self._admin_image = self.calibration_image.copy()
	# 	# 	# 	cv2.imshow("DEBUG: tvGame: camera view", self._admin_image)
	# 	# 	self.admin_interface.update_admin_image(self._admin_image)
	# 	# 	cv2.waitKey(1)
	# 	elif "init_session" in self._current_state:
	# 		for player in self._current_players:
	# 			if player.tracked is False:
	# 				self.obtain_player_id(player)
	# 	elif "game" in self._current_state:
	# 		# try:
	# 		# 	# image = self.camerasimple_proxy.getImage()
	# 		# 	# frame = np.fromstring(image.image, dtype=np.uint8)
	# 		# 	# frame = frame.reshape(image.width, image.height, image.depth)
	# 		#
	# 		# 	color, depth, _, _ = self.rgbd_proxy.getData()
	# 		# 	frame = np.fromstring(color, dtype=np.uint8)
	# 		# 	color_image = frame.reshape(480, 640, 3)
	# 		# 	depth = np.array(depth, dtype=np.uint8)
	# 		# 	depth_gray_image = depth.reshape(480, 640)
	# 		# except Ice.Exception, e:
	# 		# 	traceback.print_exc()
	# 		# 	print (e)
	# 		# 	return False
	# 		# depth_gray_image = cv2.flip(depth_gray_image, 0)
	# 		# color_image = cv2.flip(color_image, 0)
	# 		# self._admin_image = color_image.copy()
	# 		# self._admin_image = cv2.cvtColor(self._admin_image, cv2.COLOR_BGR2RGB)
	# 		# # self._admin_image = imutils.resize(self._admin_image, width=640)
	# 		# self.screen_1_factor = self.screen_1_height / float(color_image.shape[0])
	# 		#
	# 		# # self.tv_canvas = cv2.resize(self.tv_canvas, None, fx=self.screen_factor, fy=self.screen_factor,
	# 		# # 						interpolation=cv2.INTER_CUBIC)
	# 		if self._current_state == "game_getting_player":
	# 			initialicing_status = Status()
	# 			initialicing_status.currentStatus = StatusType.initializing
	# 			initialicing_status.date = datetime.now().strftime("%c")
	# 			self.gamemetrics_proxy.statusChanged(initialicing_status)
	# 			self.tv_image.show_on_second_screen()
	# 			if len(self._current_players) >0:
	# 				if self.debug:
	# 					print("Waiting to get %s players" % (len(self._current_players)))
	# 				try:
	# 					current_hand_count = self.handdetection_proxy.getHandsCount()
	#
	# 					if current_hand_count < len(self._current_players):
	# 						try:
	# 							search_roi_class = TRoi()
	# 							search_roi_class.y = 480 / 2 - 100
	# 							search_roi_class.x = 640 / 2 - 100
	# 							search_roi_class.w = 200
	# 							search_roi_class.h = 200
	# 							search_roi = (
	# 								search_roi_class.x, search_roi_class.y, search_roi_class.h, search_roi_class.w)
	#
	# 							blank_image = np.zeros((480,640,1), np.uint8)
	# 							# self._admin_image = self.draw_initial_masked_frame(color_image, search_roi)
	# 							game_image = self.draw_initial_masked_frame(blank_image , search_roi, )
	# 							game_image = cv2.resize(game_image, None, fx=self.screen_factor,
	# 													fy=self.screen_factor,
	# 													interpolation=cv2.INTER_CUBIC)
	# 							self.tv_image.set_opencv_image(game_image, False)
	# 							# self.expected_hands = self.handdetection_proxy.addNewHand(self.expected_hands,
	# 							# 														  search_roi_class)
	# 							self.handdetection_proxy.addNewHand(self.expected_hands, search_roi_class)
	# 						except Ice.Exception, e:
	# 							traceback.print_exc()
	# 							print e
	#
	# 					elif current_hand_count == self.expected_hands and self.expected_hands > 0:
	# 						self._current_state = "game_tracking"
	# 						self.reset_game()
	# 						self._game.show()
	# 						self.tv_image.hide()
	# 				except Ice.Exception, e:
	# 					traceback.print_exc()
	# 					print e
	# 			else:
	# 				image = self.tv_image.get_raw_image()
	# 				image[:] = (255, 255, 255)
	# 				# TODO: the size of the string would be substracted
	# 				image = cv2.putText(image, "ADD NEW PLAYERS", (self.screen_1_width / 2, self.screen_1_height / 2),
	# 									self.font, 1, [0, 0, 0], 2)
	# 				self.tv_image.set_opencv_image(image, False)
	# 		elif self._current_state == "game_tracking":
	# 			try:
	# 				self.hands = self.handdetection_proxy.getHands()
	# 				if len(self.hands) < self.expected_hands:
	# 					self.admin_interface.statusBar().showMessage("Hand Lost. recovering hand")
	# 					self._current_state = "game_getting_player"
	# 					self.hand_track = []
	# 					self._game.hide()
	# 					self.tv_image.show()
	# 					return
	# 				if self.debug:
	# 					self.admin_interface.statusBar().showMessage("Debug: Traking %d hands" % (len(self.hands)))
	# 				# TODO: It would be configurable from a file and dynamic
	# 				self.paint_game()
	# 			except Ice.Exception, e:
	# 				traceback.print_exc()
	# 				print e
	# 		# if self.debug:
	# 		self._admin_image = cv2.warpPerspective(self._admin_image, self.calibrator.homography,
	# 												(self.screen_1_width, self.screen_1_height))
	# 		# self.admin_interface.update_admin_image(self._admin_image)
	# 		cv2.waitKey(1)
	# 		# print "SpecificWorker.compute... in state %s with %d hands" % (self.current_state, len(self.hands))
	#
	# 		return True
	# 	elif self._current_state == "quitting":
	# 		exit(0)

	def obtain_player_id(self, player):
		if len(self._current_players) > 0:
			if self.debug:
				print("Waiting to get %s players" % (len(self._current_players)))
			try:
				current_hand_count = self.handdetection_proxy.getHandsCount()

				if current_hand_count < len(self._current_players):
					try:
						# Define ROI to obtain hand of player
						search_roi_class = TRoi()
						search_roi_class.y = 480 / 2 - 100
						search_roi_class.x = 640 / 2 - 100
						search_roi_class.w = 200
						search_roi_class.h = 200
						search_roi = (
							search_roi_class.x, search_roi_class.y, search_roi_class.h, search_roi_class.w)

						blank_image = np.zeros((480, 640, 3), np.uint8)

						# self._admin_image = self.draw_initial_masked_frame(color_image, search_roi)
						game_image = self.draw_initial_masked_frame(blank_image, search_roi, player_name=player.name)
						game_image = cv2.resize(game_image, None, fx=self.screen_factor,
												fy=self.screen_factor,
												interpolation=cv2.INTER_CUBIC)
						self.tv_image.set_opencv_image(game_image, False)
						# self.expected_hands = self.handdetection_proxy.addNewHand(self.expected_hands,
						# 														  search_roi_class)
						# self.handdetection_proxy.addNewHand(self.expected_hands, search_roi_class)
					except Ice.Exception, e:
						traceback.print_exc()
						print e

				elif current_hand_count == self.expected_hands and self.expected_hands > 0:
					self.current_state = "game_tracking"
					self.reset_game()
					self._game.show()
					self.tv_image.hide()
			except Ice.Exception, e:
				traceback.print_exc()
				print e
		else:
			image = self.tv_image.get_raw_image()
			image[:] = (255, 255, 255)
			# TODO: the size of the string would be substracted
			image = cv2.putText(image, "ADD NEW PLAYERS", (self.screen_1_width / 2, self.screen_1_height / 2),
								self.font, 1, [0, 0, 0], 2)
			self.tv_image.set_opencv_image(image, False)

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

	def add_new_player(self, name):
		self._current_players.append(name)
		# self.admin_interface.players_lcd.display(self.expected_hands)
		# self.admin_interface.remove_player_button.setEnabled(True)

	def remove_player(self, name):
		if name in self._current_players:
			del self._current_players[name]
				# self.admin_interface.remove_player_button.setEnabled(False)
		# self.admin_interface.players_lcd.display(self.expected_hands)

	#### FOR TESTING PORPOSE ONLY

	#### FOR TESTING PORPOSE ONLY

	def draw_initial_masked_frame(self, frame, search_roi, player_name):
		masked_frame = np.zeros(frame.shape, dtype="uint8")

		# masked_frame[::] = 0
		#TODO: Center Text
		template_x, template_y, template_w, template_h = search_roi
		cv2.putText(masked_frame, "PON TU MANO AQUI", (template_x - 100, template_y + template_h + 30),
					self.font, 1, [255,100, 255], 1)
		cv2.putText(masked_frame, "%s" % player_name, (template_x - 100, template_y + template_h + 60),
					self.font, 1, [255, 100, 255], 1)


		# Filled Rectangle
		masked_frame = cv2.rectangle(masked_frame, (template_x, template_y),
									 (template_x + template_w, template_y + template_h), [255, 100, 255],-1)
		# Lined rectangle
		# masked_frame = cv2.rectangle(masked_frame, (template_x, template_y),
		# 							 (template_x + template_w, template_y + template_h), [255, 255, 255])

		# alpha = 0.7
		# beta = (1.0 - alpha)
		# masked_frame = cv2.addWeighted(frame, alpha, masked_frame, beta, 0.0)
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

# =============== Methods for Component Implements ==================
# ===================================================================

	#
	# adminPauseGame
	#
	def adminPauseGame(self):
		print("adminPauseGame")
		self.game_looptogame_pause.emit()


	#
	# adminResetGame
	#
	def adminResetGame(self):
		print("adminResetGame")
		# self.reset_game()
		self.game_pausetogame_reset.emit()
		pass


	#
	# adminStartGame
	#
	def adminStartGame(self, game):
		print("adminStartGame")
		self.game_start_waittogame_init.emit()
		pass


	#
	# adminContinueGame
	#
	def adminContinueGame(self):
		print("adminContinueGame")
		self.game_pausetogame_resume.emit()



	#
	# adminEndSession
	#
	def adminEndSession(self):
		print("adminEndSession")
		self.game_start_waittosession_end.emit()
		pass


	#
	# adminStartSession
	#
	def adminStartSession(self, player):
		print("Received adminStartSession")
		new_player = Player()
		new_player.id = -1
		new_player.name = player
		new_player.tracked = False
		self._current_players.append(new_player)
		self._current_state = "init_session"
		self.session_start_waittosession_init.emit()

	#
	# adminStopGame
	#
	def adminStopGame(self):
		print("adminStopGame")
		# TODO: transition to check result state (need to be created)
		self.game_looptogame_end.emit()
		self.game_pausetogame_end.emit()




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

# ===================================================================
# ===================================================================

	def detectedTouchPoints(self, qt_touch_points):

		touch_points = []
		state_mapping = {Qt.TouchPointPressed: StateEnum.TouchPointPressed,
						 Qt.TouchPointMoved: StateEnum.TouchPointMoved,
						 Qt.TouchPointStationary: StateEnum.TouchPointPressed,
						 Qt.TouchPointReleased: StateEnum.TouchPointReleased}
		touched = False
		for qt_t_point in qt_touch_points:
			aux_point = qt_t_point.lastPos()
			if qt_t_point.state() == Qt.ToucTouchPointPressed or qt_t_point.state() == Qt.ToucTouchPointPressed:
				touched = True
			tp = TouchPoint(id=qt_t_point.id(),
											state=state_mapping[qt_t_point.state()],
											fingertip=[qt_t_point.screenPos().x(), qt_t_point.screenPos().y()],
											lastPos=[aux_point.x(), aux_point.y()])
			touch_points.append(tp)

		# Send update of metrics throught gamemetrics component interface
		self._game_metrics.set_screen_touched(touched)
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)

		# Send the touched position through touchpoints component interface
		print "TouchPoint Detected:"+str(tp)
		self.touchpoints_proxy.detectedTouchPoints(touch_points)

	def send_status_change(self, status_type):
		initialicing_status = Status()
		initialicing_status.currentStatus = status_type
		initialicing_status.date = datetime.now().isoformat()
		print("Sending %s"%str(status_type))
		self.gamemetrics_proxy.statusChanged(initialicing_status)
