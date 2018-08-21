#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
from math import floor, sqrt

import cv2
import numpy as np
from PyQt4.QtCore import QTimer, pyqtSignal, QByteArray, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QGridLayout, QApplication, QImage, QPixmap, QLabel, QPushButton, \
	QHBoxLayout

GAMES_FILE_PATH = 'resources/games.json'

class ClickableImage(QLabel):
	clicked = pyqtSignal(str)

	def __init__(self, image_path, name=None):
		super(ClickableImage, self).__init__()
		if image_path is not None and image_path != "":
			try:
				self.pixmap = QPixmap(image_path)
				if name is None:
					base = os.path.basename(image_path)
					if len(os.path.splitext(base)) > 1:
						self.name = os.path.splitext(base)[0]
			except:
				print "Problem setting the image from path: "+str(image_path)
				self.name = "Unknown"
		self.path = image_path
		if name is not None:
			self.name = name
		self.setObjectName(self.name)
		self.setText(self.name)
		self.reset_timer = QTimer()
		self.reset_timer.setSingleShot(True)
		self.reset_timer.timeout.connect(self.reset_default_image)
		self.selected = False
		self.setStyleSheet(u"border: 1px solid #ddd; border-radius: 6px;")
		self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


	def set_temp_opencv_image(self, image, delay):
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = QImage(image, image.shape[1],
					   image.shape[0], image.shape[1] * 3,
					   QImage.Format_RGB888)
		pixmap = QPixmap(image)
		self.setPixmap(pixmap)
		self.reset_timer.start(delay)

	def reset_default_image(self):
		self.setPixmap(self.pixmap)

	def to_opencv_image(self):
		image = self.pixmap.toImage()
		new_image = image.convertToFormat(QImage.Format_RGB32)

		width = image.width()
		height = image.height()
		depth = image.depth() // 8

		ptr = new_image.bits()
		s = ptr.asstring(width * height * image.depth() // 8)
		arr = np.fromstring(s, dtype=np.uint8).reshape((height, width, depth))

		return arr

	def mousePressEvent(self, event):

		self.style().unpolish(self)
		self.style().polish(self)
		self.clicked.emit(self.name)

	# def mouseReleaseEvent(self, event):

	def set_selected(self, selected):
		self.selected = selected
		if self.selected:
			self.setStyleSheet(u"border: 2px solid #92a8d1;border-radius: 8px")
		else:
			self.setStyleSheet(u"")
			self.setStyleSheet(u"border: 1px solid #ddd; border-radius: 8px;")

	def switch_selection(self):
		self.selected != self.selected
		if self.selected:
			self.setStyleSheet(u"background-color: red")
		else:
			self.setStyleSheet(u"")

	def set_image_from_base64_string(self, string):
		image_data = QByteArray.fromBase64(string)
		img = QImage()
		if img.loadFromData(image_data):
			self.setPixmap(QPixmap.fromImage(img))



class QGameLauncher(QWidget):
	def __init__(self, parent=None):
		super(QGameLauncher, self).__init__(parent)
		self.main_layout = QVBoxLayout()
		self.games_buttons_layout = QGridLayout()
		self.launch_button = QPushButton(u"Lanzar juego")
		self.launch_label = QLabel(u"")
		f = self.launch_label.font()
		f.setPointSize(6)
		self.launch_label.setFont(f)
		self.launch_button_layout = QHBoxLayout()
		self.games = {}
		self.game_grid = []
		self.game_grid_by_widget = {}
		self.game_grid_by_name = {}
		self.setLayout(self.main_layout)
		self.main_layout.addLayout(self.games_buttons_layout)
		self.launch_button_layout.addWidget(self.launch_label)
		self.launch_button_layout.addStretch()
		self.launch_button_layout.addWidget(self.launch_button)
		self.main_layout.addLayout(self.launch_button_layout)
		self.selected_game = None
		self.launch_button.clicked.connect(self.launch_game)

	def load_games_from_json(self, games_json=None):
		if games_json is None:
			with open(GAMES_FILE_PATH) as f:
				self.games = json.load(f)
		else:
			self.games=games_json


	def generate_buttons_grid(self, games_json=None):
		if len(self.games)>0:
			image_count = len(self.games)
			rows = int(floor(sqrt(image_count)))
			# columns = int(image_count / rows)
			# shuffle(images_path_list)
			for n_game, game_name in enumerate(self.games.keys()):
				row = n_game % rows
				column = int(n_game / rows)
				image_path = self.games[game_name]["path"]
				button = ClickableImage(image_path, game_name)
				if "icon" in self.games[game_name]:
					button.set_image_from_base64_string(self.games[game_name]["icon"])
				button.clicked.connect(self.game_button_clicked)
				self.games_buttons_layout.addWidget(button, row, column)
				if row < len(self.game_grid):
					self.game_grid[row].append({"name": button.name, "path": button.path, "widget": button})
				else:
					col_0 = [{"name": button.name, "path": button.path, "widget": button}]
					self.game_grid.append(col_0)
				self.game_grid_by_widget[button] = (row, column)
				self.game_grid_by_name[button.name] = (row, column)


	def get_widget_by_name(self, name):
		game_grid_coords = self.game_grid_by_name[str(name)]
		clicked_widget = self.game_grid[game_grid_coords[0]][game_grid_coords[1]]["widget"]
		return clicked_widget


	def game_button_clicked(self, name):
		clicked_widget = self.get_widget_by_name(name)
		for game in self.game_grid_by_widget.keys():
			game.set_selected(False)
		if self.selected_game != name:
			self.selected_game = name
			clicked_widget.set_selected(True)
			self.launch_label.setText(u"[+]Seleccionado juego \"%s\""%str(name))
		else:
			self.selected_game = name
			clicked_widget.set_selected(False)
			self.launch_label.setText(u"")

	def launch_game(self):
		if self.selected_game != None:
			print "Launching game "+str(self.selected_game)
			self.launch_label.setText(u"[+]Lanzando juego \"%s\""%str(self.selected_game))
		else:
			self.launch_label.setText(u"[!]No se ha seleccionado ningún juego")


	# def genera_image_tile_widget(self):
	# 	if self.image_bank is not None or len(self.image_bank) <= 0:
	# 		image_count = len(self.image_bank)
	# 		rows = int(floor(sqrt(image_count)))
	# 		# columns = int(image_count / rows)
	# 		image_ids = self.image_bank.keys()
	# 		# shuffle(image_ids)
	# 		for n_image, image_id in enumerate(image_ids):
	# 			row = n_image % rows
	# 			column = int(n_image / rows)
	# 			image = self.image_bank[image_id]
	# 			assert os.path.exists(image["path"]), "%s image path doesn't exist" % image["path"]
	# 			label = ClickableImage(image["path"], image["name"])
	# 			label.clicked.connect(self.handleLabelClicked)
	# 			self.main_layout.addWidget(label, row, column)
	# 			if row < len(self.game_grid):
	# 				self.game_grid[row].append({"name": label.name, "path": label.path, "widget": label})
	# 			else:
	# 				col_0 = [{"name": label.name, "path": label.path, "widget": label}]
	# 				self.game_grid.append(col_0)
	# 			self.game_grid_by_widget[label] = (row, column)
	# 			self.game_grid_by_name[label.name] = (row, column)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	launcher = QGameLauncher()
	launcher.load_games_from_json()
	launcher.generate_buttons_grid()
	launcher.show()
	app.exec_()

