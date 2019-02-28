# -*- coding: utf-8 -*-
"""The user interface for our app"""
import json
import math
import numbers
import os
import subprocess
import sys
from os import listdir
from os.path import isfile, join

from PyQt4.QtCore import Qt, QTimer, QPointF, pyqtSignal, QDateTime, QEvent, QObject, QRect
from PyQt4.QtGui import QApplication, QGraphicsScene, QHBoxLayout, \
	QWidget, QGraphicsView, QPixmap, QGraphicsPixmapItem, QFont, QPainter, QImage, QGraphicsTextItem
from numpy.random.mtrand import randint

# Create a class for our main window
from games.genericDragGame.ListVideoPlayer import ListVideoPlayer
from games.genericDragGame.ClockWidget import ClockWidget

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


# Reimplemented QGraphicScene to catch mouse movements for testing porposes
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
		# self.setAcceptTouchEvents(True)
		# self.pixmap().setAttribute(Qt.WA_AcceptTouchEvents)
		self.c_image = None
		self.overlay = False
		self.final_pose_x = 0
		self.final_pose_y = 0
		if draggable:
			self.create_overlary_image()

	def set_final_pose(self, x, y):
		self.final_pose_x = x
		self.final_pose_y = y

	# image with overlay
	def create_overlary_image(self):
		self.c_image = QImage(self.width, self.height, QImage.Format_ARGB32)
		painter = QPainter(self.c_image)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		painter.fillRect(self.c_image.rect(), Qt.transparent)
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
			self.setPixmap(QPixmap.fromImage(self.c_image))
		else:
			self.overlay = False
			self.setPixmap(QPixmap.fromImage(self.image))

	def resize(self, width, height):
		self.width = width
		self.height = height
		self.image = QImage(self.image_path).scaled(self.width, self.height, Qt.KeepAspectRatio)
		if self.c_image:
			self.create_overlary_image()
		if self.overlay:
			self.setPixmap(QPixmap.fromImage(self.c_image))
		else:
			self.setPixmap(QPixmap.fromImage(self.image))
			
		
	# def paint(self, painter, style, widget):
	# 	r = self.boundingRect()
	# 	p = painter.pen()
	# 	painter.drawRect(QRect(r.x(), r.y(), r.width() - p.width(), r.height() - p.width()));
	# 	super(DraggableItem, self).paint(painter, style, widget)

	def clone(self):
		return DraggableItem(self.id, self.image_path, self.width, self.height, self.draggable)


class Pointer(QObject):
	def __init__(self, id, xpos, ypos, grabbed, open_widget, closed_widget):
		super(Pointer, self).__init__()
		self._id = id
		self._grabbed = grabbed
		self._open_widget = open_widget
		self._closed_widget = closed_widget
		self._closed_widget.hide()
		self._open_widget.show()
		self._position = (xpos, ypos)
		self._taken = None
		self._lost_timer = QTimer(self)
		self._lost_timer.start(5000)

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
		self._lost_timer.start(5000)

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
		self._lost_timer.start(5000)

	@property
	def taken(self):
		return self._taken

	@taken.setter
	def taken(self, widget):
		assert (isinstance(widget,
						   QGraphicsPixmapItem) or widget == None), "Pointer.taken must be of QGraphicsPixmapItem derivated"
		self._taken = widget
		self._lost_timer.start(5000)


	@property
	def id(self):
		return self._id


	def stop(self):
		self._lost_timer.stop()


	# @property
	# def lost_ticks(self):
	# 	return self._lost_ticks
	#
	# @lost_ticks.setter
	# def lost_ticks(self, new_value):
	# 	assert (isinstance(new_value,
	# 					   int)), "Pointer.lost_ticks must be of QGraphicsPixmapItem derivated"
	# 	self._lost_ticks = new_value



class TakeDragGame(QWidget):
	touch_signal = pyqtSignal(list)
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

		self.clock = ClockWidget()
		self.clock_proxy = self.scene.addWidget(self.clock)
		self.clock.hide()
		self.clock_proxy.setPos(self.width - self.clock_proxy.boundingRect().width(), 0)
		self.clock_proxy.setZValue(60)
		self.clock.timeout.connect(self.game_timeout)


		#TODO: generalize for the game
		#TODO: do on the game initialization
		# mypath = "//home//robolab//robocomp//components//euroage-tv//components//tvGames//src//games//genericDragGame//resources//videos"
		# onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
		self.video_player = ListVideoPlayer()
		# self.video_player.set_video_list(onlyfiles)
		self._video_proxy = self.scene.addWidget(self.video_player)
		# self.video_player.reproduce_all()
		self.video_player.setFixedSize(320,240)
		self._video_proxy.setPos(1200, 100)

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
		self.clock.set_time(int(self.game_config["time"]))
		# self.clock.set_time(3)
		self.end_message.hide()
		self.setWindowState(Qt.WindowMaximized)
		self.clock.show()

	# Detecting touch events on multitouch screen
	def event(self, event):
		# print "QWidget event "+str(event.type)
		if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchEnd:
			print "TakeDragGame.event: TouchEvent Detected"
			qt_touch_points = event.touchPoints()
			self.touch_signal.emit(qt_touch_points)
		return super(TakeDragGame, self).event(event)

	def clear_scene(self):
		if self.game_config:
			for key, item in self.game_config["images"].items():
				self.scene.removeItem(item["widget"])
		if self._pointers is not None and len(self._pointers) > 0:
			for pointer in self._pointers.values():
				self.remove_pointer(pointer)

	def remove_pointer(self, pointer=None):
		# check if pointer is the class or the id of one of the pointers
		if pointer is None:
			# print "TakeDragGame.remove_pointer() : received pointer is none. Sender is " + str(self.sender().parent())
			if self.sender() is not None:
				pointer = self.sender().parent()
			else:
				return
		if isinstance(pointer, numbers.Integral):
			if pointer in self._pointers:
				the_pointer = self._pointers[pointer]
			else:
				print "TakeDragGame.remove_pointer() : WARNING unknown id " + str(pointer)
				return
		#
		elif isinstance(pointer, Pointer):
			the_pointer = pointer
		else:
			print "TakeDragGame.remove_pointer() : ERROR unexpected type "+str(type(pointer))
			return
		if the_pointer.id in self._pointers:
			print("Removing pointer id %d"%(the_pointer.id))
			the_pointer.stop()
			self.scene.removeItem(the_pointer.open_widget)
			self.scene.removeItem(the_pointer.closed_widget)
			del self._pointers[the_pointer.id]

	def show(self):
		self.show_on_second_screen()
		self.clock.start()

	def start(self):
		self.clock.start()

	def game_timeout(self):
		self.end_game(False)

	def end_game(self, value):
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



	def add_new_pointer(self, pointer_id, xpos, ypos, grab):
		print "TakeDragGame.add_new_pointer: ID=%d"%pointer_id
		open_pointer_widget = self.game_config["images"]["handOpen"]["widget"].clone()
		close_pointer_widget = self.game_config["images"]["handClose"]["widget"].clone()
		open_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
		close_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
		self._pointers[pointer_id] = Pointer(pointer_id, xpos, ypos, grab, open_pointer_widget, close_pointer_widget)
		self._pointers[pointer_id]._lost_timer.timeout.connect(self.remove_pointer)
		self.scene.addItem(self._pointers[pointer_id].open_widget)
		self.scene.addItem(self._pointers[pointer_id].closed_widget)

	def update_pointer(self, pointer_id, xpos, ypos, grab):
		if pointer_id not in self._pointers:
			self.add_new_pointer(pointer_id, xpos, ypos, grab)
		self._pointers[pointer_id].position = (xpos, ypos)
		self._pointers[pointer_id].grabbed = grab

		# The pointes is closed/grabbed
		if self._pointers[pointer_id].grabbed:
			# Check if something is taken by that pointer
			if self._pointers[pointer_id].taken is not None:
				new_xpos = xpos - self._pointers[pointer_id].taken.boundingRect().width() / 2
				new_ypos = ypos - self._pointers[pointer_id].taken.boundingRect().height() / 2

				# Set the position of the grabbed object to the center of the new position of the pointer
				self._pointers[pointer_id].taken.setPos(new_xpos, new_ypos)
			else:
				# check if there is any items unde rthe new pointer position and if it's draggable
				items = self.scene.items(QPointF(xpos, ypos))
				if len(items) > 1:
					if items[1].draggable:
						self._pointers[pointer_id].taken = items[1]
						# Set the Z position of the object take under the pointer Z value
						self._pointers[pointer_id].taken.setZValue(int(self.game_config["depth"]["mouse"]) - 1)
		# The pointer is open/ released
		else:
			# If there's something grabbed we need to release it
			if self._pointers[pointer_id].taken:
				# dropping item
				# adjust Z value
				items = self.scene.items(QPointF(xpos, ypos))
				zvalue = int(self.game_config["depth"]["image"])
				if len(items) > 1:
					# set the z value over any background image
					zvalue = zvalue + len(items) * 2
				self._pointers[pointer_id].taken.setZValue(zvalue)
				# check correct position
				xdistance = (self._pointers[pointer_id].taken.scenePos().x() + self._pointers[pointer_id].taken.width / 2) - \
							self._pointers[pointer_id].taken.final_pose_x
				ydistance = (self._pointers[pointer_id].taken.scenePos().y() + self._pointers[pointer_id].taken.height / 2) - \
							self._pointers[pointer_id].taken.final_pose_y
				distance = math.sqrt(pow(xdistance, 2) + pow(ydistance, 2))
				# If the distance to the correct position is less that a configured threshold
				if distance < int(self.game_config["difficult"]):
					# Adjust the position of the taken object to the exact correcto one
					new_xpos = self._pointers[pointer_id].taken.final_pose_x - self._pointers[pointer_id].taken.width / 2
					new_ypos = self._pointers[pointer_id].taken.final_pose_y - self._pointers[pointer_id].taken.height / 2
					self._pointers[pointer_id].taken.setPos(new_xpos, new_ypos)
					# Set the overlay of the "right" sign over the object
					self._pointers[pointer_id].taken.set_overlay(True)

					# Uodate the data of the object to avoid to be taken
					if not self._pointers[pointer_id].taken.correct_position:
						self._pointers[pointer_id].taken.correct_position = True
						self._pointers[pointer_id].taken.draggable = False
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
					if self._pointers[pointer_id].taken.correct_position:
						self._pointers[pointer_id].taken.correct_position = False
						self.correct_images = self.correct_images - 1
					self._pointers[pointer_id].taken.set_overlay(False)
				self._pointers[pointer_id].taken = None

		# self.game_config["images"]["handOpen"]["widget"].show()
		# self.game_config["images"]["handClose"]["widget"].hide()

	# self.game_config["images"]["handOpen"]["widget"].setPos(new_xpos, new_ypos)
	# self.game_config["images"]["handClose"]["widget"].setPos(new_xpos, new_ypos)

	def create_and_add_images(self):
		if self.game_config is not None:
			for image_id, item in self.game_config["images"].items():
				image_path = os.path.join(CURRENT_PATH, item["image_path"])
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
		super(TakeDragGame, self).resizeEvent(event)
		if self.game_config is None:
			return
		if event.oldSize().width() < 0 or event.oldSize().height() < 0:
			return
		self.clock_proxy.setPos(self.view.width() - self.clock_proxy.boundingRect().width() * 1.1, 0)
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
					new_finalx = item["widget"].final_pose_x * xfactor
					new_finaly = item["widget"].final_pose_y * yfactor
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

	window.init_game(os.path.join(CURRENT_PATH, 'resources/clothclean/clothgame_far.json'))

	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
