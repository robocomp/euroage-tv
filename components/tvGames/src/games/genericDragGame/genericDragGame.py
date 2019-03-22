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

from PySide2.QtCore import Signal, Qt, QObject, QTimer, QEvent, QPointF, QSize, QRectF, QUrl
from PySide2.QtGui import QImage, QPixmap, QPainter, QFont, QPen, QBrush, QColor, QPalette
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QGraphicsVideoItem
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QWidget, QHBoxLayout, QGraphicsView, \
	QGraphicsTextItem, QApplication, QGridLayout, QLabel, QStyleOption, QStyle, QGraphicsRectItem, \
	QGraphicsSimpleTextItem, QGraphicsItem
from numpy.random.mtrand import randint

# Create a class for our main window
from games.genericDragGame.CoolButton import CoolButton
from games.genericDragGame.GameWidgets import GameTopBarWidget
from games.genericDragGame.QGraphicsVideoListItem import ActionsVideoPlayer

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

GREEN_TITTLE_COLOR = "#91C69A"


class GameScreen(QWidget):
	def __init__(self, parent = None):
		super(GameScreen, self).__init__(parent)
		self._main_layout = QGridLayout()
		self.setLayout(self._main_layout)
		self.setContentsMargins(0, 0, 0, 0)
		self._main_layout.setContentsMargins(0, 0, 0, 0)
		self.setObjectName("GAME")

		self._top_bar = GameTopBarWidget()
		self._top_bar.setStyleSheet(".GameTopBarWidget{background-color: white}")
		self._top_bar.setFixedHeight(45)
		self._main_layout.addWidget(self._top_bar,0,0,1,20)
		self._game_frame = TakeDragGame(1920, 1080)
		self._game_frame.init_game(os.path.join(CURRENT_PATH, 'resources/final_game1/final_game1.json'))
		self._main_layout.addWidget(self._game_frame, 1,1, 1, 18)
		self._button1 = CoolButton(text="AYUDA", size=150)
		self._button1.set_color(QColor("Green"))
		self._button2 = CoolButton(text="TERMINAR", size=150)
		self._button1.set_color(QColor("Orange"))
		self._main_layout.addWidget(self._button1, 2,1,1,2, Qt.AlignRight)
		self._main_layout.addWidget(self._button2, 2, 3, 1, 2)
		# palette = self.palette()
		# brush = QBrush(QImage(os.path.join(CURRENT_PATH,"resources","kitchen-2165756_1920.jpg")))
		# palette.setBrush(QPalette.Background, brush)
		# self.setPalette(palette)

		# self.setStyleSheet("GameWidget {font-weight: bold; background-color: red;}")
		self.setAutoFillBackground(True)
		style_sheet_string = "GameScreen {background-image: url("+os.path.join(CURRENT_PATH,"resources","kitchen-2165756_1920.jpg")+");}"
		print(style_sheet_string)
		self.setStyleSheet(style_sheet_string)


	# def paintEvent(self, event):
	# 	painter = QPainter(self)
	# 	img = QImage(os.path.join(CURRENT_PATH,"resources","kitchen-2165756_1920.jpg"))
	# 	painter.drawImage(QRectF(0,0,self.width(),self.height()),img,QRectF(0,0,img.width(),img.height()))
	# 	super(GameWidget, self).paintEvent(event)

	def show_on_second_screen(self):
		desktop_widget = QApplication.desktop()
		if desktop_widget.screenCount() > 1:
			# TODO: set 1 to production
			second_screen_size = desktop_widget.screenGeometry(1)
			self.move(second_screen_size.left(), second_screen_size.top())
			# self.resize(second_screen_size.width(), second_screen_size.height())
			self.showFullScreen()

	def paintEvent(self, event):
		opt = QStyleOption()
		opt.init(self)
		p = QPainter(self)
		self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
		QWidget.paintEvent(self, event)




# Reimplemented QGraphicScene to catch mouse movements for testing porposes
class MyQGraphicsScene(QGraphicsScene):
	moved = Signal(int, int, int, bool)

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
		self._width = width
		self._height = height
		self.image_path = image_path
		self.draggable = draggable
		self.correct_position = False
		self.image = QImage(image_path).scaled(width, height, Qt.KeepAspectRatio)
		self.setPixmap(QPixmap.fromImage(self.image))
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
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
		self.c_image = QImage(self._width, self._height, QImage.Format_ARGB32)
		painter = QPainter(self.c_image)
		painter.setCompositionMode(QPainter.CompositionMode_Source)
		painter.fillRect(self.c_image.rect(), Qt.transparent)
		painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
		painter.drawImage(0, 0, self.image)
		painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
		aux_image = QImage(os.path.join(CURRENT_PATH, "resources/check-mark.png")).scaled(self._width / 2,
																						  self._height / 2,
																						  Qt.KeepAspectRatio)
		painter.drawImage(self._width / 4,
						  self._height / 4,
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
		self._width = width
		self._height = height
		self.image = QImage(self.image_path).scaled(self._width, self._height, Qt.KeepAspectRatio)
		if self.c_image:
			self.create_overlary_image()
		if self.overlay:
			self.setPixmap(QPixmap.fromImage(self.c_image))
		else:
			self.setPixmap(QPixmap.fromImage(self.image))

	def itemChange(self, change, value ):
		print(change, value)
		if change == QGraphicsItem.ItemPositionChange and self.scene() is not None:
			newPos = value
			rect = self.scene().sceneRect()
			if not rect.contains(newPos):
				newPos.setX(min(rect.right(), max(newPos.x(), rect.left())))
				newPos.setY(min(rect.bottom(), max(newPos.y(), rect.top())))
				return newPos
		return super(DraggableItem, self).itemChange(change, value)
			
		
	# def paint(self, painter, style, widget):
	# 	r = self.boundingRect()
	# 	p = painter.pen()
	# 	painter.drawRect(QRect(r.x(), r.y(), r.width() - p.width(), r.height() - p.width()));
	# 	super(DraggableItem, self).paint(painter, style, widget)

	def clone(self):
		return DraggableItem(self.id, self.image_path, self._width, self._height, self.draggable)

	def width(self):
		return self.boundingRect().width()

	def height(self):
		return self.boundingRect().height()


class PlayableItem(DraggableItem):
	def __init__(self, id, image_path, clip_path, width, height, draggable=False, parent=None):
		super(PlayableItem, self).__init__(id, image_path, width, height, draggable, parent)
		self._media_player = QMediaPlayer()
		self._media_player.setMuted(True)
		self._video_background = QGraphicsRectItem(self.boundingRect(), self)
		self._video_background.setZValue(-100)
		self._video_widget = QGraphicsVideoItem(self)
		self._video_widget.setZValue(100)
		self._media_player.setVideoOutput(self._video_widget)
		self._media_player.setMedia(QUrl.fromLocalFile(clip_path))
		self.stop_item()
		# self._video_widget.setSize(QSize(0, 0))
		# self.setOpacity(0.9)


	def play_item(self):
		self._video_background.setBrush(QColor("black"))
		self._video_background.update()
		self._video_widget.setSize(QSize(self.boundingRect().width()-1,self.boundingRect().height()-1))
		self._video_widget.setPos(1 , 0)
		self._media_player.play()

	def stop_item(self):
		self._video_background.setBrush(QBrush())
		self._video_background.update()
		self._video_widget.setSize(QSize(10, 10))
		self._media_player.stop()





class DestinationItem(QGraphicsRectItem):
	def __init__(self, rect, text='', parent = None):
		super(DestinationItem, self).__init__(rect, parent)
		self._text = text

	def paint(self, painter, option, widget):
		painter.save()
		painter.setBrush(QColor("black"))
		painter.drawText(self.rect(), self._text, Qt.AlignCenter | Qt.AlignVCenter)
		painter.restore()
		super(DestinationItem, self).paint(painter,option, widget)

	def width(self):
		return self.boundingRect().width()

	def height(self):
		return self.boundingRect().height()


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



class TakeDragGame(QWidget):
	touch_signal = Signal(list)
	def __init__(self, width=1920, height=1080, parent=None):
		super(TakeDragGame, self).__init__(parent)
		# ui
		self.resize(width, height)
		self._width = width
		self._height = height
		self._main_layout = QHBoxLayout()
		self.setLayout(self._main_layout)
		self._scene = MyQGraphicsScene()
		# DISCONNECT MOUSE
		self._scene.moved.connect(self.update_pointer)
		self.setCursor(Qt.BlankCursor)
		self._view = QGraphicsView()
		self._view.setMouseTracking(True)
		self._view.setScene(self._scene)
		self._view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		# TODO: Check if its better with opengl or not
		# self.view.setViewport(QtOpenGL.QGLWidget())
		self._main_layout.addWidget(self._view)
		self._main_layout.setContentsMargins(0, 0, 0, 0)

		# self.clock = ClockWidget()
		# self.clock_proxy = self.scene.addWidget(self.clock)
		# self.clock.hide()
		# self.clock_proxy.setPos(self.width - self.clock_proxy.boundingRect().width(), 0)
		# self.clock_proxy.setZValue(60)
		# self.clock.timeout.connect(self.game_timeout)
		self._pieces = []
		self._destinations = []
		self._already_set = []


		#TODO: generalize for the game
		#TODO: do on the game initialization
		# mypath = "//home//robolab//robocomp//components//euroage-tv//components//tvGames//src//games//genericDragGame//resources//videos"
		# onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]


		self.end_message = QGraphicsTextItem(u"¡Has perdido!")
		self.end_message.hide()
		self.end_message.setFont(QFont("Arial", 90, QFont.Bold))
		self.end_message.setPos(self._width / 2 - self.end_message.boundingRect().width() / 2,
								self._height / 2 - self.end_message.boundingRect().height() / 2)
		self.end_message.setZValue(60)
		self._scene.addItem(self.end_message)
		# game data
		self.total_images = 0
		self.correct_images = 0

		self._scene.setSceneRect(0, 0, width, height)
		self.grabbed = None
		self.game_config = None
		self.config = ""
		self._pointers = {}
		# self.init_game(os.path.join(CURRENT_PATH, 'resources/game1.json'))
		# print("mplayer " + "\"" + os.path.join(CURRENT_PATH, WINNING_SOUNDS[0]) + "\"")
		# subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, WINNING_SOUNDS[0]) + "\"", stdout=DEVNULL, shell=True)
		self._view.setAttribute(Qt.WA_AcceptTouchEvents)
		self._view.viewport().setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAttribute(Qt.WA_AcceptTouchEvents)

	def init_game(self, config_file='resources/game1.json'):
		self.clear_scene()
		self.game_config = None
		self.grabbed = None
		self.correct_images = 0
		self.total_images = 0
		self._pointers = {}
		self._pieces = []
		self._destinations = []
		# load config game file
		with open(os.path.join(CURRENT_PATH, config_file)) as file_path:
			self.game_config = json.load(file_path)
		# self.resize(self.game_config["size"][0], self.game_config["size"][1])
		self.create_and_add_images()
		# self.draw_position(self.scene.width()/2, self.scene.height()/2, False)
		# self.clock.set_time(int(self.game_config["time"]))
		# self.clock.set_time(3)
		self.end_message.hide()
		self.setWindowState(Qt.WindowMaximized)
		# self.clock.show()

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
				self._scene.removeItem(item["widget"])
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
			self._scene.removeItem(the_pointer.open_widget)
			self._scene.removeItem(the_pointer.closed_widget)
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
		self._scene.addItem(self._pointers[pointer_id].open_widget)
		self._scene.addItem(self._pointers[pointer_id].closed_widget)

	def update_pointer(self, pointer_id, xpos, ypos, grab):
		if pointer_id not in self._pointers:
			self.add_new_pointer(pointer_id, xpos, ypos, grab)
		self._pointers[pointer_id].position = (xpos, ypos)
		self._pointers[pointer_id].grabbed = grab

		# The pointer is closed/grabbed
		if self._pointers[pointer_id].grabbed:
			# Check if something is taken by that pointer
			# Something is taken
			if self._pointers[pointer_id].taken is not None:
				element_taken = self._pointers[pointer_id].taken
				new_xpos = xpos - element_taken.boundingRect().width() / 2
				new_ypos = ypos - element_taken.boundingRect().height() / 2

				# Set the position of the grabbed object to the center of the new position of the pointer
				element_taken.setPos(new_xpos, new_ypos)
			# Nothing taken
			else:
				# check if there is any items unde rthe new pointer position and if it's draggable
				items = self._scene.items(QPointF(xpos, ypos))
				if len(items) > 1:
					for item in items:
						if isinstance(item, PlayableItem):
							if item.draggable:
								self._pointers[pointer_id].taken = item
								# Set the Z position of the object take under the pointer Z value
								self._pointers[pointer_id].taken.setZValue(int(self.game_config["depth"]["mouse"]) - 1)
							item.play_item()
							break
		# The pointer is open/ released
		else:
			# If there's something grabbed we need to release it
			if self._pointers[pointer_id].taken:
				# dropping item
				# adjust Z value
				items = self._scene.items(QPointF(xpos, ypos))
				zvalue = int(self.game_config["depth"]["piece"])
				if len(items) > 1:
					# set the z value over any background image
					zvalue = zvalue + len(items) * 2
				self._pointers[pointer_id].taken.setZValue(zvalue)
				# check correct position
				self.adjust_to_nearest_destination(pointer_id)

				# TODO: REMOVE individual pieces check and anchoring
			# 	# Set the overlay of the "right" sign over the object
			# 	self._pointers[pointer_id].taken.set_overlay(True)
			#
			# 	# Update the data of the object to avoid to be taken
			# 	if not self._pointers[pointer_id].taken.correct_position:
			# 		self._pointers[pointer_id].taken.correct_position = True
			# 		self._pointers[pointer_id].taken.draggable = False
			# 		self.correct_images = self.correct_images + 1
			# 	# Check if game is ended and if a string is "talked"
			# 	index = randint(0, len(CONGRAT_STRING))
			# 	if self.correct_images == self.total_images:
			# 		self.end_game(True)
			# 	elif index <= len(CONGRAT_STRING):
			# 		text = CONGRAT_STRING[index]
			# 		# print("Speeching: %s"%(SPEECH_COMMAND+text))
			# 		subprocess.Popen(SPEECH_COMMAND + "\"" + text + "\"", stdout=DEVNULL, shell=True)
			# else:
				if self._pointers[pointer_id].taken.correct_position:
					self._pointers[pointer_id].taken.correct_position = False
					self.correct_images = self.correct_images - 1
				# self._pointers[pointer_id].taken.set_overlay(False)
				self._pointers[pointer_id].taken.stop_item()
				self._pointers[pointer_id].taken = None


		# self.game_config["images"]["handOpen"]["widget"].show()
		# self.game_config["images"]["handClose"]["widget"].hide()

	# self.game_config["images"]["handOpen"]["widget"].setPos(new_xpos, new_ypos)
	# self.game_config["images"]["handClose"]["widget"].setPos(new_xpos, new_ypos)

	def adjust_to_nearest_destination(self, pointer_id):
		lowest_distance = sys.maxint
		nearest_dest = None
		taken_widget = self._pointers[pointer_id].taken
		for dest in self._destinations:
			piece_center_x = taken_widget.scenePos().x() + self._pointers[
				pointer_id].taken.width() / 2.
			dest_center_x = dest.scenePos().x()+ dest.width()/2.
			xdistance = piece_center_x - dest_center_x

			piece_center_y = taken_widget.scenePos().y() + self._pointers[
				pointer_id].taken.height() / 2.
			dest_center_y = dest.scenePos().y() + dest.height() / 2.
			ydistance = piece_center_y - dest_center_y

			distance = math.sqrt(pow(xdistance, 2) + pow(ydistance, 2))
			if distance < lowest_distance:
				lowest_distance = distance
				nearest_dest = dest

		# If the distance to the correct position is less that a configured threshold
		if nearest_dest is not None and lowest_distance < int(self.game_config["difficult"]):
			# Adjust the position of the taken object to the exact correct one
			widths_diff = int((taken_widget.width() - dest.width())/2)
			heights_diff = int((taken_widget.height()- dest.height()) / 2)
			new_xpos = nearest_dest.scenePos().x() - widths_diff
			new_ypos = nearest_dest.scenePos().y() - heights_diff
			taken_widget.setPos(new_xpos, new_ypos)

	def create_and_add_images(self):
		if self.game_config is not None:
			for image_id, item in self.game_config["images"].items():
				image_path = os.path.join(CURRENT_PATH, item["image_path"])

				if "video_path" in item:
					clip_path = os.path.join(CURRENT_PATH, item["video_path"])
					new_image = PlayableItem(image_id, image_path, clip_path, item["size"][0], item["size"][1],
											 item["category"] == "piece")
				else:
					new_image = DraggableItem(image_id, image_path, item["size"][0], item["size"][1],
											  item["category"] == "piece")


				new_image.setPos(item["initial_pose"][0], item["initial_pose"][1])
				new_image.setZValue(int(self.game_config["depth"][item["category"]]))
				self.game_config["images"][image_id]["widget"] = new_image
				if item["category"] != "mouse":
					self._scene.addItem(new_image)
				if item["category"] == "piece":
					dest_image = DestinationItem(new_image.boundingRect(), str(item["index"]))
					dest_image.setPos(item["final_pose"][0], item["final_pose"][1])
					self._pieces.append(new_image)
					self._destinations.append(dest_image)
					self.total_images = self.total_images + 1
					self._scene.addItem(dest_image)



	def resizeEvent(self, event):
		# skip initial entry
		self._view.fitInView(self._scene.itemsBoundingRect(), Qt.KeepAspectRatio)
		self._scene.setSceneRect(self._scene.itemsBoundingRect())
		super(TakeDragGame, self).resizeEvent(event)
		# if self.game_config is None:
		# 	return
		# if event.oldSize().width() < 0 or event.oldSize().height() < 0:
		# 	return
		# # self.clock_proxy.setPos(self.view.width() - self.clock_proxy.boundingRect().width() * 1.1, 0)
		# self.end_message.setPos(self.view.width() / 2 - self.end_message.boundingRect().width() / 2,
		# 						self.view.height() / 2 - self.end_message.boundingRect().height() / 2)
		# # images
		# xfactor = float(event.size().width()) / float(event.oldSize().width())
		# yfactor = float(event.size().height()) / float(event.oldSize().height())
		# for key, item in self.game_config["images"].items():
		# 	# TODO: resize called before widget creation
		# 	if "widget" in item:
		# 		# update size
		# 		new_xsize = item["widget"].width * xfactor
		# 		new_ysize = item["widget"].height * yfactor
		# 		item["widget"].resize(new_xsize, new_ysize)
		# 		# update position
		# 		new_xpos = float(item["widget"].scenePos().x()) * xfactor
		# 		new_ypos = float(item["widget"].scenePos().y()) * yfactor
		# 		item["widget"].setPos(new_xpos, new_ypos)
		# 		# update final pose
		# 		if item["widget"].draggable:
		# 			new_finalx = item["widget"].final_pose_x * xfactor
		# 			new_finaly = item["widget"].final_pose_y * yfactor
		# 			item["widget"].set_final_pose(new_finalx, new_finaly)

	def show_on_second_screen(self):
		desktop_widget = QApplication.desktop()
		if desktop_widget.screenCount() > 1:
			# TODO: set 1 to production
			second_screen_size = desktop_widget.screenGeometry(1)
			self.move(second_screen_size.left(), second_screen_size.top())
			# self.resize(second_screen_size.width(), second_screen_size.height())
			self.showFullScreen()


def main():
	# Again, this is boilerplate, it's going to be the same on
	# almost every app you write
	app = QApplication(sys.argv)
	the_label = GameScreen()
	the_label.show()

	# main_widget = GameWidget()
	# main_widget.show_on_second_screen()
	# window = TakeDragGame(1920, 1080)
	# window.show()



	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
