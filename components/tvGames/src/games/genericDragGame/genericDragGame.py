# -*- coding: utf-8 -*-
"""The user interface for our app"""
import json
import math
import os
import subprocess
import sys
import time

# Create a class for our main window
from subprocess import call

from PyQt4.QtCore import Qt, QTimer, QPointF, pyqtSignal, QDateTime, QEvent
from PyQt4.QtGui import QApplication, QGraphicsScene, QHBoxLayout, \
	QWidget, QGraphicsView, QPixmap, QGraphicsPixmapItem, QLabel, QFont, QPainter, QImage, QGraphicsTextItem
from numpy.random.mtrand import randint

try:
	from subprocess import DEVNULL  # py3k
except ImportError:
	import os

	DEVNULL = open(os.devnull, 'wb')

CURRENT_PATH = os.path.dirname(__file__)

CONGRAT_STRING = ["¡Vas muy bien!", "¡Sigue así!", "¡Genial!", "¡Estupendo!", "¡Fabulóso!", "¡Maravilloso!", "¡Ánimo!",
				  "¡Lo estás haciendo muy bien!"]
WINNING_SOUNDS = ["resources/sounds/happy1.mp3", "resources/sounds/happy2.mp3"]
LOST_SOUNDS = ["resources/sounds/sad1.mp3", "resources/sounds/sad2-2.mp3"]
SPEECH_COMMAND = "gtts es "

#Reimplemented QGraphicScene to catch mouse movements for testing porposes
class MyQGraphicsScene(QGraphicsScene):
	moved = pyqtSignal(int, int, int, bool)

	def mousePressEvent(self, event):
		self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

	def mouseMoveEvent(self, event):
		self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

	def mouseReleaseEvent(self, event):
		self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

# It's the item to be moved on the game
class DraggableItem(QGraphicsPixmapItem):

	def __init__(self, id, image_path, width, height, draggable=False, parent=None):
		super(DraggableItem, self).__init__(parent)
		self.id = id
		self.width = width
		self.height = height
		self.image_path = image_path
		self.draggable = draggable
		self.correct_position = False
		self.image = QImage(image_path).scaled(width, height, Qt.KeepAspectRatio)
		self.setPixmap(QPixmap.fromImage(self.image))
		self.setAcceptTouchEvents(True)
		# self.pixmap().setAttribute(Qt.WA_AcceptTouchEvents)
		self.cimage = None
		self.overlay = False
		if draggable:
			self.create_overlary_image()

	def set_final_pose(self, x, y):
		self.final_posex = x
		self.final_posey = y

	# image with overlay
	def create_overlary_image(self):
		self.cimage = QImage(self.width, self.height, QImage.Format_ARGB32)
		painter = QPainter(self.cimage)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		painter.fillRect(self.cimage.rect(), Qt.transparent)
		painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
		painter.drawImage(0, 0, self.image)
		painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
		aux_image = QImage(os.path.join(CURRENT_PATH, "resources/check-mark.png")).scaled(self.width / 2,
																						  self.height / 2,
																						  Qt.KeepAspectRatio)
		painter.drawImage(self.width / 4,
						  self.height / 4,
						  aux_image)
		painter.end()

	def set_overlay(self, value):
		if value:
			self.overlay = True
			self.setPixmap(QPixmap.fromImage(self.cimage))
		else:
			self.overlay = False
			self.setPixmap(QPixmap.fromImage(self.image))

	def resize(self, width, height):
		self.width = width
		self.height = height
		self.image = QImage(self.image_path).scaled(self.width, self.height, Qt.KeepAspectRatio)
		if self.cimage:
			self.create_overlary_image()
		if self.overlay:
			self.setPixmap(QPixmap.fromImage(self.cimage))
		else:
			self.setPixmap(QPixmap.fromImage(self.image))

	def clone(self):
		return DraggableItem(self.id, self.image_path, self.width, self.height, self.draggable)


class Pointer(object):
	def __init__(self, id, xpos, ypos, grabbed, open_widget, closed_widget):
		self._id = id
		self._grabbed = grabbed
		self._open_widget = open_widget
		self._closed_widget = closed_widget
		self._closed_widget.hide()
		self._open_widget.show()
		self._position = (xpos, ypos)
		self._taken = None

	@property
	def grabbed(self):
		return self._grabbed

	@grabbed.setter
	def grabbed(self, value):
		assert isinstance(value, bool), "Pointer.grabbed must be boolean"
		self._grabbed = value
		if self._grabbed:
			self._closed_widget.show()
			self._open_widget.hide()
			# self.game_config["images"]["handClose"]["widget"].show()
			# self.game_config["images"]["handOpen"]["widget"].hide()
		else:
			self._closed_widget.hide()
			self._open_widget.show()

	@property
	def open_widget(self):
		return self._open_widget

	@open_widget.setter
	def open_widget(self, widget):
		assert isinstance(widget, QGraphicsPixmapItem), "Pointer.open_widget must be of QGraphicsPixmapItem derivated"
		self._open_widget = widget

	@property
	def closed_widget(self):
		return self._closed_widget

	@closed_widget.setter
	def closed_widget(self, widget):
		assert isinstance(widget, QGraphicsPixmapItem), "Pointer.closed_widget must be of QGraphicsPixmapItem derivated"
		self._closed_widget = widget

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, position):
		new_xpos = position[0] - self._open_widget.boundingRect().width() / 2
		new_ypos = position[1] - self._open_widget.boundingRect().height() / 2
		self._position = (new_xpos, new_ypos)
		self._open_widget.setPos(new_xpos, new_ypos)
		self._closed_widget.setPos(new_xpos, new_ypos)

	@property
	def taken(self):
		return self._taken

	@taken.setter
	def taken(self, widget):
		assert (isinstance(widget,
						   QGraphicsPixmapItem) or widget == None), "Pointer.taken must be of QGraphicsPixmapItem derivated"
		self._taken = widget


class TakeDragGame(QWidget):
	def __init__(self, width=1920, height=1080, parent=None):
		super(TakeDragGame, self).__init__(parent)
		# ui
		self.resize(width, height)
		self.width = width
		self.height = height
		self.main_layout = QHBoxLayout()
		self.setLayout(self.main_layout)
		self.scene = MyQGraphicsScene()
		# DISCONNECT MOUSE
		self.scene.moved.connect(self.update_pointer)
		self.setCursor(Qt.BlankCursor)
		self.view = QGraphicsView()
		self.view.setMouseTracking(True)
		self.view.setScene(self.scene)
		self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		# TODO: Check if its better with opengl or not
		# self.view.setViewport(QtOpenGL.QGLWidget())
		self.main_layout.addWidget(self.view)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_clock)
		self.clock = QGraphicsTextItem("00:00")
		self.clock.hide()
		self.clock.setFont(QFont("Arial", 70, QFont.Bold))
		self.clock.setPos(self.width - self.clock.boundingRect().width(), 0)
		self.clock.setZValue(60)
		self.scene.addItem(self.clock)
		self.end_message = QGraphicsTextItem(u"¡Has perdido!")
		self.end_message.hide()
		self.end_message.setFont(QFont("Arial", 90, QFont.Bold))
		self.end_message.setPos(self.width / 2 - self.end_message.boundingRect().width() / 2,
								self.height / 2 - self.end_message.boundingRect().height() / 2)
		self.end_message.setZValue(60)
		self.scene.addItem(self.end_message)
		# game data
		self.total_images = 0
		self.correct_images = 0
		self.time = None
		self.scene.setSceneRect(0, 0, width, height)
		self.grabbed = None
		self.game_config = None
		self.config = ""
		self._pointers = {}
		# self.init_game(os.path.join(CURRENT_PATH, 'resources/game1.json'))
		# print("mplayer " + "\"" + os.path.join(CURRENT_PATH, WINNING_SOUNDS[0]) + "\"")
		# subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, WINNING_SOUNDS[0]) + "\"", stdout=DEVNULL, shell=True)
		self.view.setAttribute(Qt.WA_AcceptTouchEvents)
		self.view.viewport().setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAttribute(Qt.WA_AcceptTouchEvents)

	def init_game(self, config_file='resources/game1.json'):
		self.clear_scene()
		self.game_config = None
		self.grabbed = None
		self.correct_images = 0
		self.total_images = 0
		self._pointers = {}
		# load config game file
		with open(os.path.join(CURRENT_PATH, config_file)) as file_path:
			self.game_config = json.load(file_path)
		self.resize(self.game_config["size"][0], self.game_config["size"][1])
		self.create_and_add_images()
		# self.draw_position(self.scene.width()/2, self.scene.height()/2, False)
		self.time = int(self.game_config["time"])
		self.end_message.hide()
		self.setWindowState(Qt.WindowMaximized)
		self.clock.show()
		self.update_clock()
	
	def event(self, event):
		# print "QWidget event "+str(event.type)
		if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchEnd:
			touch_points = event.touchPoints()
			print touch_points
			for tp in touch_points:
				if tp.state() == Qt.TouchPointPressed or tp.state() == Qt.TouchPointMoved:
					self.update_pointer(tp.id(), tp.pos().x(), tp.pos().y(), True)
				if tp.state() == Qt.TouchPointReleased:
					self.update_pointer(tp.id(), tp.pos().x(), tp.pos().y(), False)
		return super(TakeDragGame, self).event(event)

	def clear_scene(self):
		if self.game_config:
			for key, item in self.game_config["images"].items():
				self.scene.removeItem(item["widget"])
		if len(self._pointers) > 0 and self._pointers is not None:
			for pointer in self._pointers.values():
				self.scene.removeItem(pointer.open_widget)
				self.scene.removeItem(pointer.closed_widget)

	def show(self):
		self.show_on_second_screen()
		self.timer.start(1000)

	def end_game(self, value):
		self.timer.stop()
		if value:
			self.end_message.setHtml(u"<font color='green'>¡Has ganado!</font>")
			index = randint(0, len(WINNING_SOUNDS))
			file = WINNING_SOUNDS[index]
			subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, file) + "\"", stdout=DEVNULL, shell=True)
		else:
			self.end_message.setHtml(u"<font color='red'>¡Has perdido!</font>")
			index = randint(0, len(LOST_SOUNDS))
			file = LOST_SOUNDS[index]
			subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, file) + "\"", stdout=DEVNULL, shell=True)
		self.clock.hide()
		self.end_message.show()
		#        self.scene.update()
		#        time.sleep(3)
		self.clear_scene()

	def update_clock(self):
		time_string = QDateTime.fromTime_t(self.time).toString("mm:ss")
		self.clock.setPlainText(time_string)
		if self.time <= 0:
			self.end_game(False)
		self.time = self.time - 1

	def update_pointer(self, id, xpos, ypos, grab):
		if id not in self._pointers:
			open_pointer_widget = self.game_config["images"]["handOpen"]["widget"].clone()
			close_pointer_widget = self.game_config["images"]["handClose"]["widget"].clone()
			open_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
			close_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
			self._pointers[id] = Pointer(id, xpos, ypos, grab, open_pointer_widget, close_pointer_widget)
			self.scene.addItem(self._pointers[id].open_widget)
			self.scene.addItem(self._pointers[id].closed_widget)
		self._pointers[id].position = (xpos, ypos)
		self._pointers[id].grabbed = grab

		# The pointes is closed/grabbed
		if self._pointers[id].grabbed:
			# Check if something is taken by that pointer
			if self._pointers[id].taken is not None:
				new_xpos = xpos - self._pointers[id].taken.boundingRect().width() / 2
				new_ypos = ypos - self._pointers[id].taken.boundingRect().height() / 2

				# Set the position of the grabbed object to the center of the new position of the pointer
				self._pointers[id].taken.setPos(new_xpos, new_ypos)
			else:
				# check if there is any items unde rthe new pointer position and if it's draggable
				items = self.scene.items(QPointF(xpos, ypos))
				if len(items) > 1:
					if items[1].draggable:
						self._pointers[id].taken = items[1]
						# Set the Z position of the object take under the pointer Z value
						self._pointers[id].taken.setZValue(int(self.game_config["depth"]["mouse"]) - 1)
		# The pointer is open/ released
		else:
			# If there's something grabbed we need to release it
			if self._pointers[id].taken:
				# dropping item
				# adjust Z value
				items = self.scene.items(QPointF(xpos, ypos))
				zvalue = int(self.game_config["depth"]["image"])
				if len(items) > 1:
					# set the z value over any background image
					zvalue = zvalue + len(items) * 2
				self._pointers[id].taken.setZValue(zvalue)
				# check correct position
				xdistance = (self._pointers[id].taken.scenePos().x() + self._pointers[id].taken.width / 2) - \
							self._pointers[id].taken.final_posex
				ydistance = (self._pointers[id].taken.scenePos().y() + self._pointers[id].taken.height / 2) - \
							self._pointers[id].taken.final_posey
				distance = math.sqrt(pow(xdistance, 2) + pow(ydistance, 2))
				# If the distance to the correct position is less that a configured threshold
				if distance < int(self.game_config["difficult"]):
					# Adjust the position of the taken object to the exact correcto one
					new_xpos = self._pointers[id].taken.final_posex - self._pointers[id].taken.width / 2
					new_ypos = self._pointers[id].taken.final_posey - self._pointers[id].taken.height / 2
					self._pointers[id].taken.setPos(new_xpos, new_ypos)
					# Set the overlay of the "right" sign over the object
					self._pointers[id].taken.set_overlay(True)

					# Uodate the data of the object to avoid to be taken
					if not self._pointers[id].taken.correct_position:
						self._pointers[id].taken.correct_position = True
						self._pointers[id].taken.draggable = False
						self.correct_images = self.correct_images + 1
					# Check if game is ended and if a string is "talked"
					index = randint(0, len(CONGRAT_STRING))
					if self.correct_images == self.total_images:
						self.end_game(True)
					elif index <= len(CONGRAT_STRING):
						text = CONGRAT_STRING[index]
						# print("Speeching: %s"%(SPEECH_COMMAND+text))
						subprocess.Popen(SPEECH_COMMAND + "\"" + text + "\"", stdout=DEVNULL, shell=True)
				else:
					if self._pointers[id].taken.correct_position:
						self._pointers[id].taken.correct_position = False
						self.correct_images = self.correct_images - 1
					self._pointers[id].taken.set_overlay(False)
				self._pointers[id].taken = None

			# self.game_config["images"]["handOpen"]["widget"].show()
			# self.game_config["images"]["handClose"]["widget"].hide()

		# self.game_config["images"]["handOpen"]["widget"].setPos(new_xpos, new_ypos)
		# self.game_config["images"]["handClose"]["widget"].setPos(new_xpos, new_ypos)

	def create_and_add_images(self):
		if self.game_config is not None:
			for image_id, item in self.game_config["images"].items():
				image_path = os.path.join(CURRENT_PATH, item["path"])
				new_image = DraggableItem(image_id, image_path, item["size"][0], item["size"][1],
										  item["category"] == "image")
				new_image.setPos(item["initial_pose"][0], item["initial_pose"][1])
				new_image.setZValue(int(self.game_config["depth"][item["category"]]))
				self.game_config["images"][image_id]["widget"] = new_image
				if item["category"] != "mouse":
					self.scene.addItem(new_image)
				if item["category"] == "image":
					new_image.set_final_pose(item["final_pose"][0], item["final_pose"][1])
					self.total_images = self.total_images + 1

	def resizeEvent(self, event):
		# skip initial entry
		if event.oldSize().width() < 0 or event.oldSize().height() < 0:
			return
		super(TakeDragGame, self).resizeEvent(event)
		self.clock.setPos(self.view.width() - self.clock.boundingRect().width() * 1.1, 0)
		self.end_message.setPos(self.view.width() / 2 - self.end_message.boundingRect().width() / 2,
								self.view.height() / 2 - self.end_message.boundingRect().height() / 2)
		# images
		xfactor = float(event.size().width()) / float(event.oldSize().width())
		yfactor = float(event.size().height()) / float(event.oldSize().height())
		for key, item in self.game_config["images"].items():
			# TODO: resize called before widget creation
			if "widget" in item:
				# update size
				new_xsize = item["widget"].width * xfactor
				new_ysize = item["widget"].height * yfactor
				item["widget"].resize(new_xsize, new_ysize)
				# update position
				new_xpos = float(item["widget"].scenePos().x()) * xfactor
				new_ypos = float(item["widget"].scenePos().y()) * yfactor
				item["widget"].setPos(new_xpos, new_ypos)
				# update final pose
				if item["widget"].draggable:
					new_finalx = item["widget"].final_posex * xfactor
					new_finaly = item["widget"].final_posey * yfactor
					item["widget"].set_final_pose(new_finalx, new_finaly)

	def show_on_second_screen(self):
		desktop_widget = QApplication.desktop()
		if desktop_widget.screenCount() > 1:
			second_screen_size = desktop_widget.screenGeometry(1)
			self.move(second_screen_size.left(), second_screen_size.top())
			# self.resize(second_screen_size.width(), second_screen_size.height())
			self.showFullScreen()


def main():
	# Again, this is boilerplate, it's going to be the same on
	# almost every app you write
	app = QApplication(sys.argv)
	window = TakeDragGame(1920, 1080)
	window.show()

	window.init_game(os.path.join(CURRENT_PATH, 'resources/game4.json'))

	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
