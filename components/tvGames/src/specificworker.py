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
import traceback
import yaml
from datetime import datetime

import cv2
import numpy as np
from PySide2.QtCore import Qt, QTimer, QTranslator, QLocale
from PySide2.QtWidgets import QApplication

from games.draganddropgame.draganddropgame import GameScreen
from genericworker import *
from libs.utils import init_touchscreen_device
# from modules.AdminInterface import AdminInterface
from modules.CalibrationStateMachine import ManualCalibrationStateMachine
from modules.HandMouse import MultiHandMouses
from modules.QImageWidget import QImageWidget

stream = open("src/config.yml", 'r')
config = yaml.load(stream)

LANGUAGES = {
	"Spanish": "src/i18n/es_ES.qm",
	"Portuguese": "src/i18n/pt_PT.qm"
}

FILE_PATH = os.path.dirname(__file__)


class Player:
	"""
	Class containing the needed information of the Player of the Game.
	"""
	def __init__(self, player_id=-1, name=""):
		self.player_id = player_id
		self.name = name
		self.tracked = False

#  	struct Position
# 	{
# 		 float x;
# 		 float y;
# 	};
# 	struct Metrics
# 	{
# 		 string currentDate;
# 		 Position pos;
# 		 int numScreenTouched;
# 		 int numHandClosed;
# 		 int numHelps;
# 		 int numChecked;
# 		 int numHits;
# 		 int numFails;
# 	};


class GameMetrics(Metrics):
	"""
	Class and method to take control of the tracked metrics of the game played.
	This class directly inherit from the Metrics provided by ice interface GameMetrics.ice
	"""
	def __init__(self):
		super(GameMetrics, self).__init__()
		self.currentDate = datetime.now().isoformat()
		self.numHelps = 0
		self.numChecked = 0
		self.numHits = 0
		self.numFails = 0
		self.numHandClosed = 0
		self.numScreenTouched = 0
		self.pos = Position()
		self.pos.x = -1
		self.pos.y = -1

	def increment_helps(self, quantity=1):
		"""
		Increments the value of helps requested by the player during the game
		:param quantity: by default it's an increment of 1, but other values can be specified.
		:return: None
		"""
		self.numHelps+=quantity

	def increment_checked(self, quantity=1):
		"""
		Increments the value of checks requested by the player during the game
		:param quantity: by default it's an increment of 1, but other values can be specified.
		:return: None
		"""
		self.numChecked+=quantity

	def increment_hits(self, quantity=1):
		"""
		Increments the value of hits got by the player during the game
		:param quantity: by default it's an increment of 1, but other values can be specified.
		:return: None
		"""
		self.numHits+=quantity

	def increment_fails(self, quantity=1):
		"""
		Increments the value of fails got by the player during the game
		:param quantity: by default it's an increment of 1, but other values can be specified.
		:return: None
		"""
		self.numFails+=quantity

	def set_screen_touched(self, touched=True, pos=None):
		"""
		Method to keep track of the state of the touchs on the screen and its positions.
		:param touched: True or False to set if the screen have been touched
		:param pos: Position class to be stored.
		:return:
		"""
		self.screenTouched = touched
		if pos:
			self.pos.x = pos.x
			self.pos.y = pos.y

	def set_hand_closed(self, closed=True, pos=None):
		"""
		Method to keep track of the state of the hand and its positions.
		:param closed: True or False to set if the hand have been closed
		:param pos: Position class to be stored.
		:return:
		"""
		self.handClosed = closed
		if pos:
			self.pos.x = pos.x
			self.pos.y = pos.y


class GameStartData:
	def __init__(self):
		self.name = None
		self.duration = -1



class SpecificWorker(GenericWorker):
	"""
	Main class of the tvGames component.
	This class doesn't implement the game logic but the state machine logic to work in sync with gameManager
	and the needed methods to keep track of the metrics of the played game.
	The current game implementation can be found on src/games/draganddropgame/draganddropgame.py
	The configuration for the different variations of this game can be found on src/games/resources
	"""
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.__language = None
		self.__translator = None
		self.translate_to(config["default_language"])
		self._current_players = []
		self.hands = []
		self.font = cv2.FONT_HERSHEY_SIMPLEX

		self.hide()
		self.debug = True

		# TODO: Probably deprecated. No image should be shown on the same computer than tvGame
		self.tv_image = QImageWidget()

		self.mouse_grab = False


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
		self._current_game =  None

		# game name and path
		self._available_games = {}
		self._game = GameScreen()
		self._game.show_on_second_screen()

		# self._admin_image = None
		self._mouse_release_point = None

		self._game_metrics = GameMetrics()

		# TODO: Testing only. Remove on production.
		# self.adminStartSession("Juan Lopez")
		# TODO: Probably deprecated. No image should be shown on the same computer than tvGame
		# self.tv_image.show_on_second_screen()

		self.application_machine.start()

	def __del__(self):
		print ('SpecificWorker destructor')

	def update_game_selection(self):
		"""
		This method use the self._current_game_name (it's set by the gameManager) through the adminStartGame method
		to create, connect signal an start the selected game.
		:return:
		"""
		if self._current_game is not None:
			self._game = GameScreen(None, self._game_screen_width, self._game_screen_height)
			self._game.game_frame.touch_signal.connect(self.detectedTouchPoints)
			self._game.help_clicked.connect(self.game_help_clicked)
			self._game.check_clicked.connect(self.game_check_clicked)
			self._game.score_update.connect(self.game_score_update)
			self._game.game_win.connect(self.t_game_loop_to_game_won)
			self._game.game_lost.connect(self.t_game_loop_to_game_lost)
			self.reset_game()


	def game_help_clicked(self):
		"""
		Slot to update help Metrics and send it to gameManager
		:return:
		"""
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numHelps += 1
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)

	def game_check_clicked(self):
		"""
		Slot to update check Metrics and send it to gameManager
		:return:
		"""
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numChecked += 1
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)

	def game_score_update(self, win, fail):
		"""
		Slot to update win/fails Metrics por the pieces of the game and send it to gameManager
		:param win: Pieces on the right position
		:param fail: Pieces on the wrong position
		"""
		self._game_metrics.currentDate = datetime.now().isoformat()
		self._game_metrics.numFails = fail
		self._game_metrics.numHits = win
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)


	def reset_game(self):
		"""
		Method to reset and reconfigure teh current game.
		The configuration file is stored at the self._available_games attribute amd this is filled in by
		the load_available_games in this same file
		:return:
		"""
		config_path = self._available_games[str(self._current_game.name)]
		self._game_metrics = GameMetrics()
		self._game.init_game(config_path, self._current_game.duration)

	def mouse_pressed_on_tv(self, point):
		"""
		TODO: Probably deprecated method.
		"""
		self.mouse_grab = True
		print("Mouse pressed")

	def mouse_released_on_tv(self, point):
		"""
		TODO: Probably deprecated method.
		"""
		self.mouse_grab = False
		self._mouse_release_point = point
		print("Mouse released")

	def translate_to(self, language):
		app = QApplication.instance()
		if language in LANGUAGES:
			self.__language = language
			translation_file = LANGUAGES[language]
		else:
			self.__language = "Spanish"
		if self.__translator is None:
			self.__translator = QTranslator()
		else:
			app.removeTranslator(self.__translator)
		if self.__translator.load(translation_file):
			print("-------Loading translation")
			if app is not None:
				print("-------Translating")
				app.installTranslator(self.__translator)
			else:
				print("-------Could not find app instance")
				self.__translator = None
		else:
			print("-------couldn't load translation")
			self.__translator = None

	def setParams(self, params):
		"""
		Set the params loaded from the config file.
		The path where the games are expected to be found can be changed on config file.
		:param params:
		:return:
		"""
		if "games_path" in params:
			self.load_available_games(params["games_path"])
		return True


# =============== Slots methods for State Machine ===================
# ===================================================================
	#
	# sm_game_machine
	#
	@QtCore.Slot()
	def sm_game_machine(self):
		"""
		game_machine => app_end;
		:return:
		"""
		print("Entered state game_machine")

	#
	# sm_app_end
	#
	@QtCore.Slot()
	def sm_app_end(self):
		"""
		game_machine => app_end;
		:return:
		"""
		print("Entered state app_end")
		QApplication.quit()


	#
	# sm_session_start_wait
	#
	@QtCore.Slot()
	def sm_session_start_wait(self):
		"""
		session_start_wait => session_init;
		session_end => session_start_wait;
		:return:
		"""
		print("Entered state session_start_wait")
		init_touchscreen_device()
		# TODO: Test only. Remove on production
		# self.t_session_start_wait_to_session_init.emit()
		self.send_status_change(StatusType.waitingSession)


	#
	# sm_game_end
	#
	@QtCore.Slot()
	def sm_game_end(self):
		"""
        game_end => game_lost;
        game_end => game_won;
		game_loop => game_end;
        game_pause => game_end;
		:return:
		"""
		print("Entered state game_end")
		won = self._game.end_game()
		if won:
			self.t_game_end_to_game_won.emit()
		else:
			self.t_game_end_to_game_lost.emit()



	#
	# sm_game_init
	#
	@QtCore.Slot()
	def sm_game_init(self):
		"""
        game_init => game_loop;
		game_start_wait => game_init;
		:return:
		"""
		print("Entered state game_init")
		self._game = None
		self.update_game_selection()
		self._game.show_on_second_screen()
		self.t_game_init_to_game_loop.emit()

	#
	# sm_game_loop
	#
	@QtCore.Slot()
	def sm_game_loop(self):
		"""
        game_loop => game_loop, game_pause, game_won, game_lost, game_end;
		game_init => game_loop;
        game_pause => game_loop;
        game_resume => game_loop;
		:return:
		"""
		self._game_metrics.currentDate = datetime.now().isoformat()
		self.gamemetrics_proxy.metricsObtained(self._game_metrics)
		print("Entered state game_loop")
		self.send_status_change(StatusType.playingGame)
		QTimer.singleShot(200, self.t_game_loop_to_game_loop)

	#
	# sm_game_lost
	#
	@QtCore.Slot()
	def sm_game_lost(self):
		"""
        game_lost => game_start_wait;
        game_loop => game_lost;
        game_end => game_lost;
		:return:
		"""
		print("Entered state game_lost")
		# TODO: Only for 1 screen playing. It lets the lost screen to last 3 seconds on screen.
		QTimer.singleShot(3000, lambda: self.send_status_change(StatusType.lostGame))
		QTimer.singleShot(200, self.t_game_lost_to_game_start_wait)



	#
	# sm_game_pause
	#
	@QtCore.Slot()
	def sm_game_pause(self):
		"""
		game_pause => game_loop;
        game_pause => game_reset;
        game_pause => game_resume;
        game_pause => game_end;
		game_loop => game_pause
		:return:
		"""
		print("Entered state game_pause")
		self._game.pause_game()
		self.send_status_change(StatusType.pausedGame)


	#
	# sm_game_reset
	#
	@QtCore.Slot()
	def sm_game_reset(self):
		"""
		game_reset => game_start_wait;
		game_pause => game_reset;
		:return:
		"""
		print("Entered state game_reset")
		self._game.hide()
		self.send_status_change(StatusType.resetedGame)
		self.t_game_reset_to_game_start_wait.emit()

	#
	# sm_game_resume
	#
	@QtCore.Slot()
	def sm_game_resume(self):
		"""
		game_resume => game_loop;
		game_pause => game_resume;
		:return:
		"""
		print("Entered state game_resume")
		self._game.resume_game()
		self.t_game_resume_to_game_loop.emit()

	#
	# sm_game_start_wait
	#
	@QtCore.Slot()
	def sm_game_start_wait(self):
		"""
		game_start_wait => game_start_wait;
        game_start_wait => game_init;
        game_start_wait => session_end
		game_won => game_start_wait;
		game_lost => game_start_wait;
        game_lost => game_start_wait;
        game_won => game_start_wait;
        game_reset => game_start_wait;
		session_init => game_start_wait;
		:return:
		"""
		print("Entered state game_start_wait")

		# TODO: Test only. Remove on production
		# self.t_game_start_wait_to_game_init.emit()
		self.send_status_change(StatusType.waitingGame)
		QTimer.singleShot(200, self.t_game_start_wait_to_game_start_wait)



	#
	# sm_game_won
	#
	@QtCore.Slot()
	def sm_game_won(self):
		"""
		game_won => game_start_wait;
		game_loop => game_won;
        game_end => game_won;
		:return:
		"""
		print("Entered state game_won")
		# TODO: Only for 1 screen playing. It lets the win screen to last 3 seconds on screen.
		QTimer.singleShot(3000, lambda: self.send_status_change(StatusType.wonGame))
		QTimer.singleShot(200, self.t_game_won_to_game_start_wait)


	#
	# sm_session_end
	#
	@QtCore.Slot()
	def sm_session_end(self):
		"""
		game_start_wait => session_end;
        session_end => session_start_wait;
		:return:
		"""
		print("Entered state session_end")
		self.send_status_change(StatusType.endSession)
		self._game.pause_game()
		self._game.hide()
		self._game = None
		QTimer.singleShot(100, self.t_session_end_to_session_start_wait)


	#
	# sm_session_init
	#
	@QtCore.Slot()
	def sm_session_init(self):
		"""
		session_start_wait => session_init;
        session_init => game_start_wait;
		:return:
		"""
		print("Entered state session_init")
		self.send_status_change(StatusType.initializingSession)



	#
	# sm_player_acquisition_init
	#
	@QtCore.Slot()
	def sm_player_acquisition_init(self):
		"""
		player_acquisition_init => player_acquisition_loop;
		:return:
		"""
		print("Entered state player_acquisition_init")
		self.send_status_change(StatusType.initializingSession)
		self.t_player_acquisition_init_to_player_acquisition_loop.emit()


	#
	# sm_player_acquisition_loop
	#
	@QtCore.Slot()
	def sm_player_acquisition_loop(self):
		"""
		player_acquisition_init => player_acquisition_loop;
        player_acquisition_loop => player_acquisition_loop;
        player_acquisition_loop => player_acquisition_ended;
		:return:
		"""
		print("Entered state player_acquisition_loop")
		acquired = True
		for player in self._current_players:
			if player.tracked is False:
				acquired = False
				#TODO: NOASTRA => uncomment obtain_player and remove
				#self.obtain_player_id(player)
				self.current_state = "game_tracking"

		#TODO: testing only. Remove on production
		acquired=True

		if acquired:
			self.t_player_acquisition_loop_to_player_acquisition_ended.emit()
		else:
			QTimer.singleShot(1000 / 33, self.t_player_acquisition_loop_to_player_acquisition_loop)

	#
	# sm_player_acquisition_ended
	#
	@QtCore.Slot()
	def sm_player_acquisition_ended(self):
		"""
		player_acquisition_loop => player_acquisition_ended;
		:return:
		"""
		print("Entered state player_acquisition_ended")
		self.tv_image.hide()
		self.send_status_change(StatusType.readySession)
		# TODO: Testing only. remove on production
		self.t_session_init_to_game_start_wait.emit()


# =================================================================
# =================================================================



	def load_available_games(self, path):
		"""
		Given a path this method look for .json files that contains a valid game.
		TODO: It's only checked that the title key exists. More checks could be done. Like the paths to the needed images/videos
		:param path:
		:return:
		"""
		self._available_games = {}
		full_path = os.path.join(FILE_PATH, path)
		# r=root, d=directories, f = files
		for root, dirs, files in os.walk(full_path):
			for file in files:
				if file.endswith(".json"):
					full_file_path = os.path.join(root, file)
					with open(full_file_path) as file_path:
						game_config = json.load(file_path)
						if "title" in game_config:
							self._available_games[game_config["title"]] = full_file_path

	#TODO: NOASTRA => not used on no handDetecion requirement
	def obtain_player_id(self, player):
		"""
		TODO: Probably deprecated. Hand detection and tracking was moved to IntegratedHand component and is not currently in use.
		This method is intended to look for hands of the players. It's currently not in use.
		:param player:
		:return:
		"""
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
					except Ice.Exception as e:
						traceback.print_exc()
						print (e)

				elif current_hand_count == self.expected_hands and self.expected_hands > 0:
					self.current_state = "game_tracking"
					self.reset_game()
					self._game.show()
					self.tv_image.hide()
			except Ice.Exception as e:
				traceback.print_exc()
				print (e)
		else:
			image = self.tv_image.get_raw_image()
			image[:] = (255, 255, 255)
			# TODO: the size of the string would be substracted
			image = cv2.putText(image, "ADD NEW PLAYERS", (self.screen_1_width / 2, self.screen_1_height / 2),
								self.font, 1, [0, 0, 0], 2)
			self.tv_image.set_opencv_image(image, False)

	def paint_game(self):
		"""
		TODO: Probably deprecated. Hand detection and tracking was moved to IntegratedHand component and is not currently in use.
		This method check for detected hands and try to paint the center of mass of the hand on the admin image (deprecated)
		and update the pointer on the game.
		:return:
		"""
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
		"""
		TODO: Deprecated
		"""
		ret = np.resize(p, (len(p) + 1, 1))
		ret[-1][0] = 1.
		return ret

	def fromHomogeneus(self, p):
		"""
		TODO: Deprecated
		"""
		return np.true_divide(p[:-1], p[-1])

	def login_executed(self, accepted):
		"""
		TODO: Deprecated
		"""
		if accepted:
			self.current_state = "calibrating"
			self.tv_image.show_on_second_screen()
			self.login_widget.hide()

	def add_new_player(self, name):
		"""
		TODO: Possibly Deprecated
		:return:
		"""
		self._current_players.append(name)
		# self.admin_interface.players_lcd.display(self.expected_hands)
		# self.admin_interface.remove_player_button.setEnabled(True)

	def remove_player(self, name):
		"""
		TODO: Possibly Deprecated
		:return:
		"""
		if name in self._current_players:
			del self._current_players[name]
				# self.admin_interface.remove_player_button.setEnabled(False)
		# self.admin_interface.players_lcd.display(self.expected_hands)

	#### FOR TESTING PORPOSE ONLY

	#### FOR TESTING PORPOSE ONLY


	def draw_initial_masked_frame(self, frame, search_roi, player_name):
		"""
		TODO: Possibly Deprecated
		Draws information over the received frame
		:return:
		"""
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
		"""
		TODO: Possibly Deprecated
		Draws information over the received frame
		:return:
		"""
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
		"""
		TODO: Possibly Deprecated
		Draws information over the received frame
		:return:
		"""
		if point is not None:
			# Draw center mass
			cv2.circle(frame, tuple(point), 7, color, 2)
		# cv2.putText(frame, 'Center', tuple(point), self.font, 0.5, (255, 255, 255), 1)
		return frame


	def draw_hand_track(self, frame):
		"""
		TODO: Possibly Deprecated
		Draws information over the received frame
		:return:
		"""
		if len(self.hand_track) > 2:
			for i in np.arange(1, len(self.hand_track)):
				p1 = self.hand_track[i]
				p0 = self.hand_track[i - 1]
				cv2.line(frame, tuple(p0), tuple(p1), (0, 0, 255), 3)
		return frame

# =============== Methods for Component Implements ==================
# ===================================================================

	#
	# adminChangeLanguage
	#
	def AdminGame_adminChangeLanguage(self, language):
		#
		# implementCODE
		#
		print("Asked to change language to %s"%language)
		self.translate_to(language)


	#
	# adminPauseGame
	#
	def AdminGame_adminPauseGame(self):
		"""
		Implementation of the communication required for adminPauseGame.
		This will just generate the transition to the State Machine pause state.
		:return:
		"""
		print("adminPauseGame")
		self.t_game_loop_to_game_pause.emit()

	#
	# adminStopApp
	#
	def AdminGame_adminStopApp(self):
		"""
		Implementation of the communication required for adminStopApp.
		This will just generate the transition to the State Machine pause state.
		:return:
		"""
		"""
		Implementation of the communication required for adminStopApp.
		This will just generate the transition to the State Machine app_end state.
		:return:
		"""
		print("adminStopApp")
		self.t_game_machine_to_app_end.emit()


	#
	# adminResetGame
	#
	def AdminGame_adminResetGame(self):
		"""
		Implementation of the communication required for adminResetGame.
		This will just generate the transition to the State Machine game_reset state.
		:return:
		"""
		print("adminResetGame")
		# self.reset_game()
		self.t_game_pause_to_game_reset.emit()
		pass


	#
	# adminStartGame
	#
	def AdminGame_adminStartGame(self, game, duration):
		"""
		Implementation of the communication required for adminStartGame.
		This will just generate the transition to the State Machine game_init state.
		:return:
		"""
		print("adminStartGame")
		self._current_game = GameStartData()
		self._current_game.name = game
		self._current_game.duration = duration
		self.activateWindow()
		self.t_game_start_wait_to_game_init.emit()


	#
	# adminContinueGame
	#
	def AdminGame_adminContinueGame(self):
		"""
		Implementation of the communication required for adminContinueGame.
		This will just generate the transition to the State Machine game_resume state.
		:return:
		"""
		print("adminContinueGame")
		self.activateWindow()
		self.t_game_pause_to_game_resume.emit()



	#
	# adminEndSession
	#
	def AdminGame_adminEndSession(self):
		"""
		Implementation of the communication required for adminEndSession.
		This will just generate the transition to the State Machine session_end state.
		:return:
		"""
		print("adminEndSession")
		self.t_game_start_wait_to_session_end.emit()
		pass


	#
	# adminStartSession
	#
	def AdminGame_adminStartSession(self, player):
		"""
		Implementation of the communication required for adminStartSession.
		This will create a new player with the provided name and will generate the transition to the State Machine session_init state.
		:return:
		"""
		print("Received adminStartSession")
		new_player = Player()
		new_player.player_id = -1
		new_player.name = player
		new_player.tracked = False
		self._current_players.append(new_player)
		self.t_session_start_wait_to_session_init.emit()

	#
	# adminStopGame
	#
	def AdminGame_adminStopGame(self):
		"""
		Implementation of the communication required for adminStopGame.
		This will just generate the transition to the State Machine pause state.
		:return:
		"""
		print("adminStopGame")
		# TODO: transition to check result state (need to be created)
		self.t_game_loop_to_game_end.emit()
		self.t_game_pause_to_game_end.emit()

	#
	# reloadConfig
	#
	def CommonBehavior_reloadConfig(self):
		#
		# implementCODE
		#
		pass


	#
	# setPeriod
	#
	def CommonBehavior_setPeriod(self, period):
		#
		# implementCODE
		#
		pass


	#
	# getState
	#
	def CommonBehavior_getState(self):
		ret = State()
		#self.touchpoints_proxy.detectedTouchPoints(touch_points)
		# implementCODE
		#
		return ret


	#
	# setParameterList
	#
	def CommonBehavior_setParameterList(self, l):
		#
		# implementCODE
		#
		pass


	#
	# timeAwake
	#
	def CommonBehavior_timeAwake(self):
		ret = int()
		#
		# implementCODE
		#
		return ret


	#
	# getParameterList
	#
	def CommonBehavior_getParameterList(self):
		ret = ParameterList()
		#
		# implementCODE
		#
		return ret


	#
	# killYourSelf
	#
	def CommonBehavior_killYourSelf(self):
		#
		# implementCODE
		#
		pass


	#
	# getPeriod
	#
	def CommonBehavior_getPeriod(self):
		ret = int()
		#
		# implementCODE
		#
		return ret


	#
	# launchGame
	#
	def TvGames_launchGame(self, name):
		#
		# implementCODE
		#
		pass

# ===================================================================
# ===================================================================

	def detectedTouchPoints(self, touch_points):
		"""
		Slot to store the detected touchpoints on the Metrics and send to gameManager
		:param touch_points: structure with the information of the points touched.
		:return:
		"""
		print("tvGames detected %d"%len(touch_points))
		if len(touch_points) > 0:
			state_mapping = {Qt.TouchPointPressed: StateEnum.TouchPointPressed,
							 Qt.TouchPointMoved: StateEnum.TouchPointMoved,
							 Qt.TouchPointStationary: StateEnum.TouchPointPressed,
							 Qt.TouchPointReleased: StateEnum.TouchPointReleased}
			for tpoint in touch_points:
				tpoint.state = state_mapping[tpoint.state]

			# Send update of metrics throught gamemetrics component interface
			if touch_points[-1].state == StateEnum.TouchPointPressed:
				self._game_metrics.numScreenTouched += 1
			self._game_metrics.pos.x = touch_points[-1].fingertip[0]
			self._game_metrics.pos.y = touch_points[-1].fingertip[1]
			self.gamemetrics_proxy.metricsObtained(self._game_metrics)

			# self.touchpoints_proxy.detectedTouchPoints(touch_points)


	def send_status_change(self, status_type):
		"""
		TODO: This would be replaced by a required petition from gameManager for each possible status.

		:param status_type:
		:return:
		"""
		initializing_status = Status()
		initializing_status.currentStatus = status_type
		initializing_status.date = datetime.now().isoformat()
		print("Sending %s"%str(status_type))
		self.gamemetrics_proxy.statusChanged(initializing_status)

