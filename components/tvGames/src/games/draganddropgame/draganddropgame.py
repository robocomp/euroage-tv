# -*- coding: utf-8 -*-
"""The user interface for our app"""
import json
import math
import numbers

import cv2
import numpy as np
import os
import random
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
    QGraphicsSimpleTextItem, QGraphicsItem, QStackedLayout, QFrame, QDialog, QVBoxLayout
from PySide2.QtCore import QRect, Qt, QSize, QPoint
from PySide2.QtGui import QRegion, QColor, QIcon, QPixmap, QPainter, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, \
    QHBoxLayout

from numpy.random.mtrand import randint


try:
    from games.draganddropgame.gamewidgets import GameTopBarWidget, GameScores, CoolButton, GameScreenLogo
    from games.draganddropgame.videoplayers import ActionsVideoPlayer
except:
    from gamewidgets import GameTopBarWidget, CoolButton, GameScores
    from videoplayers import ActionsVideoPlayer

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os

    DEVNULL = open(os.devnull, 'wb')

CURRENT_PATH = os.path.dirname(__file__)

CONGRAT_STRINGS = ["¡Vas muy bien!", "¡Sigue así!", "¡Genial!", "¡Buen trabajo!", "¡Estupendo!", "¡Fabulóso!", "¡Maravilloso!", "¡Ánimo!",
                  "¡Lo estás haciendo muy bien!", "¡Continua!"]
RECHECK_STRINGS = ["Quizás deberías revisar tus piezas", "Puedes comprobar tus resultados", "Recuerda que puedes pulsar el botón de Ayuda", "mmmm",
                   "Algunas secuencias son un poco complicadas", "¿Crees que podría ser de otra forma?"]
RIGHT_STRINGS = ["¡No está mal! ¡Continua!", "¡Vas bien, pero recuerda que puedes comprobar!", "¡Vas bien, pero recuerda que puedes pulsar ayuda!"]
WRONG_STRINGS = ["¡No está mal! Pero puedes revisar algunas piezas", "Puedes hacer algunos cambios", "Piensa si la secuencia tiene sentido"]
# WINNING_SOUNDS = ["../resources/common/sounds/happy1.mp3", "../resources/common/sounds/happy2.mp3"]
WINNING_SOUNDS = ["../resources/common/sounds/happy1.mp3"]
# LOST_SOUNDS = ["../resources/common/sounds/sad1.mp3", "../resources/common/sounds/sad2-2.mp3"]
LOST_SOUNDS = ["../resources/common/sounds/sad2-2.mp3"]
SPEECH_COMMAND = "gtts es "

GREEN_TITTLE_COLOR = "#91C69A"

# Create a class for our main window
class GameScreen(QWidget):
    game_win = Signal()
    game_lost = Signal()
    help_clicked = Signal()
    check_clicked = Signal()
    score_update = Signal(int, int)
    def __init__(self, parent = None, width=1920, height=1080):
        super(GameScreen, self).__init__(parent)

        self._main_layout = QStackedLayout()
        self._game_widget = QFrame()
        self._game_layout = QGridLayout()
        self._game_widget.setLayout(self._game_layout)
        self._main_layout.addWidget(self._game_widget)
        self.setLayout(self._main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        self._game_layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("GAME")

        self._top_bar = GameTopBarWidget()
        self._top_bar.setStyleSheet(".GameTopBarWidget{background-color: white}")
        self._top_bar.setFixedHeight(45)
        self._game_layout.addWidget(self._top_bar, 0, 0, 1, 20)
        self._game_frame = TakeDragGame(width, height)
        self._game_layout.addWidget(self._game_frame, 1, 1, 1, 18)
        self._help_button = CoolButton(text="AYUDA", size=150, image_path=os.path.join(CURRENT_PATH,"..","resources","common","button","justQuestion.png"))
        self._help_button.set_color(QColor("Green"))
        self._check_button = CoolButton(text="REVISAR", size=150, image_path=os.path.join(CURRENT_PATH,"..","resources","common","button","checked.png"))
        self._help_button.set_color(QColor("Orange"))
        self._game_layout.addWidget(self._help_button, 2, 1, 1, 2, Qt.AlignRight)
        self._game_layout.addWidget(self._check_button, 2, 3, 1, 2)
        self._logos = GameScreenLogo()
        self._game_layout.addWidget(self._logos,2,13,1,6,Qt.AlignLeft )

        self._video_player = ActionsVideoPlayer()
        self._video_player.setWindowTitle("Ayuda")

        # palette = self.palette()
        # brush = QBrush(QImage(os.path.join(CURRENT_PATH,"resources","kitchen-2165756_1920.jpg")))
        # palette.setBrush(QPalette.Background, brush)
        # self.setPalette(palette)

        # self.setStyleSheet("GameWidget {font-weight: bold; background-color: red;}")
        self.setAutoFillBackground(True)
        style_sheet_string = "GameScreen {background-image: url("+os.path.join(CURRENT_PATH,"..","resources","common", "kitchen-2165756_1920.jpg")+");}"
        self.setStyleSheet(style_sheet_string)

        self.end_message = QLabel(u"¡Has perdido!")

        self.end_message.setFont(QFont("Arial", 90, QFont.Bold))
        self.end_message.setAlignment(Qt.AlignCenter)

        self._game_config = {}
        self._main_layout.addWidget(self.end_message)
        self._main_layout.setCurrentIndex(0)
        self._scores_close_timer = QTimer()
        self._scores_dialog = QDialog()


        self._top_bar.clock_timeout.connect(self.game_timeout)
        self._game_frame.score_update.connect(self._top_bar.set_scores)
        self._game_frame.score_update.connect(self.show_big_scores)
        self._game_frame.game_win.connect(self.end_game)
        self._check_button.clicked.connect(self._game_frame.check_scores)
        self._check_button.clicked.connect(self.check_clicked)
        self._help_button.clicked.connect(self.show_help)
        self._help_button.clicked.connect(self.help_clicked)
        self._game_frame.score_update.connect(self.score_update)




    def show_big_scores(self, value1, value2):
        # aux_layout = QVBoxLayout()
        # dialog.setLayout(aux_layout)
        # aux_layout.a
        aux_scores = GameScores(self._scores_dialog)
        aux_scores.set_score(1, value1)
        aux_scores.set_score(0, value2)
        desktop_widget = QApplication.desktop()
        aux_scores.setFixedSize(500, 280)
        aux_scores.setMaximumSize(500, 280)
        self._scores_dialog.setFixedSize(aux_scores.size())
        if desktop_widget.screenCount() > 1:
            screen_rect = desktop_widget.screenGeometry(1)
        else:
            screen_rect = desktop_widget.screenGeometry(0)
        newx = screen_rect.left() + (screen_rect.width() - self._scores_dialog.width()) / 2
        newy = screen_rect.top() + (screen_rect.height() - self._scores_dialog.height()) / 2
        self._scores_dialog.move(newx, newy)
        self._scores_dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._scores_close_timer.timeout.connect(self._scores_dialog.close)
        self._scores_close_timer.start(2000)
        self._scores_dialog.exec_()



    @property
    def game_frame(self):
        return self._game_frame

    def show_help(self):
        # TODO: add some feedback to the user when there's no video to play.
        if self._video_player.current_status() != QMediaPlayer.State.PlayingState:
            pieces = self._game_frame.already_set_pieces()
            self._video_player.clear()
            for piece in pieces:
                self._video_player.add_action(piece.id, piece.clip_path, piece.current_destination.index)
            if len(pieces) > 0:
                self._video_player.show_on_second_screen()
                print(self._video_player.current_status())
                self._video_player.play_all_actions_as_inserted()


    def game_timeout(self):
        self.end_game()

    def end_game(self):
        result = False
        if self._game_frame.check_win():
            result = True
            self.end_message.setText(u"<font color='green'>¡Has ganado!</font>")
            index = randint(0, len(WINNING_SOUNDS))
            file = WINNING_SOUNDS[index]
            subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, file) + "\"", stdout=DEVNULL, shell=True)
            self.game_win.emit()
        else:
            self.end_message.setText(u"<font color='red'>¡Has perdido!</font>")
            index = randint(0, len(LOST_SOUNDS))
            file = LOST_SOUNDS[index]
            subprocess.Popen("mplayer " + "\"" + os.path.join(CURRENT_PATH, file) + "\"", stdout=DEVNULL, shell=True)
            self._game_frame._update_scores()
            self.game_lost.emit()
        self._game_frame.end_game()
        self._main_layout.setCurrentIndex(1)
        return result

    def pause_game(self):
        self._top_bar.pause_clock()

    def resume_game(self):
        self._top_bar.resume_clock()


    def init_game(self, full_path):
        if isinstance(full_path, str):
            full_path = os.path.join(CURRENT_PATH, full_path)
            if os.path.isfile(full_path):
                with open(full_path) as file_path:
                    self._game_config = json.load(file_path)
                self._game_frame.init_game(full_path)
                self._top_bar.set_game_name(self._game_config["title"])
                self._top_bar.set_time(int(self._game_config["time"]))
                self._top_bar.start_clock()




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
    
    def __init__(self,*args, **kwargs):
        super(MyQGraphicsScene, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

    def mouseMoveEvent(self, event):
        self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

    def mouseReleaseEvent(self, event):
        self.moved.emit(-1, event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)



# It's the item to be moved on the game
class DraggableItem(QGraphicsPixmapItem):

    def __init__(self, id, image_path,  parent=None):
        super(DraggableItem, self).__init__(parent)
        self.id = id
        self.__image_path = None
        self.image_path = image_path
        self.correct_position = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.c_image = None
        self.overlay = None
        # self.setAcceptTouchEvents(True)
        # self.pixmap().setAttribute(Qt.WA_AcceptTouchEvents)


    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def image_path(self):
        return self.__image_path

    @image_path.setter
    def image_path(self, image_path):
        if image_path is not None:
            if self.image_path is not None:
                self.image = QImage(image_path).scaled(self.image.width(), self.image.height(), Qt.KeepAspectRatio)
            else:
                self.image = QImage(image_path).scaled(320, 240, Qt.KeepAspectRatio)

            self.setPixmap(QPixmap.fromImage(self.image))
            self.__image_path = image_path

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, image):
        if image is not None:
            self.__image = image
            self.setPixmap(QPixmap.fromImage(image))

    @property
    def width(self):
        return self.boundingRect().width()

    @width.setter
    def width(self, value):
        if value>0:
            current_ratio = self.height/self.width
            new_height = value * current_ratio
            self.resize(value, new_height)


    @property
    def height(self):
        return self.boundingRect().height()

    @height.setter
    def height(self, value):
        if value>0:
            current_ratio = self.width/self.height
            new_width = value * current_ratio
            self.resize(new_width, value)


    def set_overlay(self, value):
        if value:
            self.overlay = True
            self.setPixmap(QPixmap.fromImage(self.c_image))
        else:
            self.overlay = False
            self.setPixmap(QPixmap.fromImage(self.image))

    def resize(self, width, height):
        current_pos = self.pos()
        self.image = QImage(self.image_path).scaled(width, height, Qt.KeepAspectRatio)
        self.setPos(current_pos)
        # if self.c_image:
        #     self.create_overlary_image()
        # if self.overlay:
        #     self.setPixmap(QPixmap.fromImage(self.c_image))
        # else:
        #     self.setPixmap(QPixmap.fromImage(self.image))

    def itemChange(self, change, value ):
        # Check that the piece is kept inside the scene rect
        if change == QGraphicsItem.ItemPositionChange and self.scene() is not None:
            newPos = value
            rect = self.scene().sceneRect()
            # If it doen't it position the piece on a valid position inside the scene rect
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
        return DraggableItem(self.id, self.image_path)




class PieceItem(DraggableItem):
    def __init__(self, id, image_path, clip_path, width, height, title, parent=None):
        super(PieceItem, self).__init__(id, image_path, width, height, parent)
        self._clip_path = clip_path

        self._media_player = QMediaPlayer()
        self._media_player.setMuted(True)
        self._video_background = QGraphicsRectItem(self.boundingRect(), self)
        self._video_background.setZValue(-100)
        self._video_widget = QGraphicsVideoItem(self)
        self._video_widget.setZValue(100)
        self._media_player.setVideoOutput(self._video_widget)
        self._media_player.setMedia(QUrl.fromLocalFile(self._clip_path))
        self._media_player.mediaStatusChanged.connect(self._update_media_status)
        self._media_player.stateChanged.connect(self._update_state)
        self._hide_video()

        self._label = QGraphicsTextItem(self) # Label
        self._set_label(title.upper(), "margin:10px; font-weight: bold; font-size: " +str(self.width()/18)+"pt;  background-color:#91C69A; border-radius: 20pt; border-top-right-radius: 5px; border-bottom-left-radius: 5px;") # Nombre
        self._label.setY(self.height()-10) # Posicionar abajo
        # self._label.setY(-20) # Posicionar arriba
        self._label.setTextWidth(self.width())
        self._final_destination = None
        self._current_destination = None
        self.c_image = None
        self.overlay = False
        self.create_overlary_image()
        # self._video_widget.setSize(QSize(0, 0))
        # self.setOpacity(0.9)

    @property
    def final_destination(self):
        return self._final_destination

    @final_destination.setter
    def final_destination(self, dest):
        self._final_destination = dest

    @property
    def current_destination(self):
        return self._current_destination

    @current_destination.setter
    def current_destination(self, new_dest):
        self._current_destination = new_dest


    @property
    def clip_path(self):
        return self._clip_path

    @clip_path.setter
    def clip_path(self, path):
        self._clip_path = path


    def play_item(self):
        self._media_player.play()

    def _show_video(self):
        self._video_background.setBrush(QColor("black"))
        self._video_background.update()
        self._video_widget.setSize(QSize(self.boundingRect().width() - 1, self.boundingRect().height() - 1))
        self._video_widget.setPos(1, 0)

    def stop_item(self):
        self._media_player.stop()

    def _hide_video(self):
        self._video_background.setBrush(QBrush())
        self._video_background.update()
        self._video_widget.setSize(QSize(10, 10))

    def _set_label(self, text, style):
        self._label.setHtml("<div style='"+style+"'><center><p>"+text+"</p></center>")

    def is_playing(self):
        return self._media_player.state() == QMediaPlayer.PlayingState

    def _update_media_status(self, status):
        print(status)
        # if status == QMediaPlayer.EndOfMedia:
        # 	self._hide_video()

    def _update_state(self, state):
        print(state)
        if state == QMediaPlayer.PlayingState:
            self._show_video()
        if state == QMediaPlayer.StoppedState:
            self._hide_video()

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

# Replacement for the PieceItem (working implementation for video piece)
class QOpencvGraphicsVideoItem(DraggableItem):
    def __init__(self, id, image_path, video_path, title, parent=None):
        super(QOpencvGraphicsVideoItem, self).__init__(id, image_path, parent)
        self._video_source = None
        self._video_path = None
        self._video_frame = None
        if video_path is not None:
            self.set_video_path(video_path)
        self._play_timer = QTimer()
        self._play_timer.timeout.connect(self.show_next_frame)
        self._old_image = None
        self._title = title
        self._label = QGraphicsTextItem(self)  # Label
        self._set_label(self._title.upper(), "margin:10px; font-weight: bold; font-size: " + str(
            self.width / 18) + "pt;  background-color:#91C69A; border-radius: 20pt; border-top-right-radius: 5px; border-bottom-left-radius: 5px;")  # Nombre
        self._label.setY(self.height - 10)  # Posicionar abajo
        # self._label.setY(-20) # Posicionar arriba
        self._label.setTextWidth(self.width)

        self._final_destination = None
        self._current_destination = None

    @property
    def width(self):
        return super(QOpencvGraphicsVideoItem, self).width

    @width.setter
    def width(self, value):
        super(QOpencvGraphicsVideoItem, self.__class__).width.fset(self, value)
        self._set_label(self._title.upper(), "margin:10px; font-weight: bold; font-size: " + str(
            self.width / 18) + "pt;  background-color:#91C69A; border-radius: 20pt; border-top-right-radius: 5px; border-bottom-left-radius: 5px;")
        self._label.setY(self.height - 10)
        self._label.setTextWidth(self.width)



    @property
    def final_destination(self):
        return self._final_destination

    @final_destination.setter
    def final_destination(self, dest):
        self._final_destination = dest

    @property
    def current_destination(self):
        return self._current_destination

    @current_destination.setter
    def current_destination(self, new_dest):
        self._current_destination = new_dest

    @property
    def clip_path(self):
        return self._video_path

    @clip_path.setter
    def clip_path(self, path):
        self._video_path = path


    def set_video_path(self, path):
        assert os.path.isfile(path), "No valid path provided %s" % str(path)
        self._video_source = cv2.VideoCapture(path)
        self._video_path = path

    def play(self):
        self._old_image = self.image_path
        self._play_timer.start(1000 / 30)

    def show_next_frame(self):
        if (self._video_source.isOpened() == False):
            print("Error opening video stream or file")
            return
        ret, frame = self._video_source.read()
        if ret == True:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_height, frame_width, channels = frame.shape

            # Calculate ratios of the video frame readed and holder for it (self)
            frame_ratio = frame_width / float(frame_height)
            image_ratio = self.width / float(self.height)

            # create a black umage of the size of the holder
            background_size = (int(self.height), int(self.width), 3)
            blank_image = np.zeros(background_size, np.uint8)
            # blank_image[:] = (255, 255, 255)

            # based on the ratio difference between video frame and holder, the video is resized to the largest available size in holder (width or height)
            if frame_ratio > image_ratio:
                resized_frame = cv2.resize(frame, dsize=(int(self.width), int(round(self.width / frame_ratio))),
                                           interpolation=cv2.INTER_CUBIC)
            else:
                resized_frame = cv2.resize(frame, dsize=(int(round(self.height * frame_ratio)), int(self.height)),
                                           interpolation=cv2.INTER_CUBIC)

            height_offset = int((background_size[0] - resized_frame.shape[0]) / 2)

            # video frame image is added over the black image
            blank_image[height_offset:height_offset + resized_frame.shape[0], 0:resized_frame.shape[1]] = resized_frame

            # final image converted to QImage
            self._video_frame = QImage(blank_image, blank_image.shape[1], blank_image.shape[0], blank_image.shape[1] * 3, QImage.Format_RGB888)

            self._video_frame = self._video_frame.scaled(self.width, self.height, Qt.KeepAspectRatio)
            self.image = self._video_frame

        else:
            self.stop()

    def stop(self):
        self._play_timer.stop()
        self.image_path = self._old_image
        # Re-set the video source for a new playing)
        self.set_video_path(self._video_path)

    def pause(self):
        self._play_timer.stop()

    def hide_video(self):
        self.image_path = self._old_image

    def show_video(self):
        self.show_next_frame()

    def is_playing(self):
        return self._play_timer.isActive()

    def _set_label(self, text, style):
        self._label.setHtml("<div style='"+style+"'><center><p>"+text+"</p></center>")


class DestinationItem(QGraphicsRectItem):
    def __init__(self, rect, index, parent = None):
        super(DestinationItem, self).__init__(rect, parent)
        self._text = str(index)
        self._index = index
        self._contained_piece = None

    def paint(self, painter, option, widget):
        painter.save()
        painter.setBrush(QColor("black"))
        font = painter.font()
        font.setPointSize(100)
        painter.setFont(font)
        painter.drawText(self.rect(), self._text, Qt.AlignCenter | Qt.AlignVCenter)
        painter.restore()
        super(DestinationItem, self).paint(painter,option, widget)

    def empty(self):
        if self._contained_piece is None:
            return True
        else:
            return False

    @property
    def contained_piece(self):
        return self._contained_piece

    @contained_piece.setter
    def contained_piece(self, piece):
        self._contained_piece = piece
        if piece is not None:
            piece.current_destination = self

    @property
    def width(self):
        return self.boundingRect().width()

    @property
    def height(self):
        return self.boundingRect().height()

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, ind):
        self._index = ind
        self._text = str(ind)



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

class MyTouchPoint:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class MyQGraphicsView(QGraphicsView):
    touch_signal = Signal(list)
    state_mapping = { QEvent.MouseButtonPress: Qt.TouchPointPressed,
                      QEvent.MouseMove: Qt.TouchPointMoved,
                      QEvent.MouseButtonRelease: Qt.TouchPointReleased}


    def __init__(self, parent = None):
        super(MyQGraphicsView, self).__init__(parent)
        self.setAttribute(Qt.WA_AcceptTouchEvents)


    def viewportEvent(self, event):
        # print "QWidget event "+str(event.type)
        touchs_to_detect = [QEvent.TouchBegin, QEvent.TouchUpdate, QEvent.TouchEnd]
        # WARN: Single finger t
        mouses_to_detect = [QEvent.MouseButtonRelease, QEvent.MouseMove]
        touched = False
        touch_points = []
        if event.type() in touchs_to_detect:
            qt_touch_points = event.touchPoints()
            for qt_t_point in qt_touch_points:
                if qt_t_point.state() == Qt.TouchPointPressed or qt_t_point.state() == Qt.TouchPointMoved or Qt.TouchPointReleased:
                    touched = True
                    tp = MyTouchPoint(id=qt_t_point.id(),
                                    state=qt_t_point.state(),
                                    fingertip=[qt_t_point.screenPos().x(), qt_t_point.screenPos().y()],
                                    lastPos=[])
                    touch_points.append(tp)
            # print ("TakeDragGame.event: TouchEvent Detected %s" % (str(event.type())))
        elif event.type() in mouses_to_detect and event.source() == Qt.MouseEventSynthesizedByQt:
            # print ("TakeDragGame.event: Mouse/Touch Detected %s" % (str(event.type())))
            my_touch_point = MyTouchPoint(id=0, state=self.state_mapping[event.type()], fingertip=[event.screenPos().x(), event.screenPos().y()], lastPos=[])
            touch_points.append(my_touch_point)
            touched = True
        if touched:
            self.touch_signal.emit(touch_points)
        return super(MyQGraphicsView, self).viewportEvent(event)

class TakeDragGame(QWidget):
    touch_signal = Signal(list)
    score_update = Signal(int, int)
    game_win = Signal()
    def __init__(self, width=1920, height=1080, parent=None):
        super(TakeDragGame, self).__init__(parent)
        # ui
        self.resize(width, height)
        self._width = width
        self._height = height
        self._main_layout = QHBoxLayout()
        self.setLayout(self._main_layout)
        self._scene = MyQGraphicsScene(0,0, width, height)
        # DISCONNECT MOUSE
        self._scene.moved.connect(self.update_pointer)
        self.setCursor(Qt.BlankCursor)
        self._view = MyQGraphicsView()
        self._view.touch_signal.connect(self.touch_signal)
        self._view.setMouseTracking(True)
        self._view.setScene(self._scene)
        self._view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # TODO: Check if its better with opengl or not
        # self.view.setViewport(QtOpenGL.QGLWidget())
        self._main_layout.addWidget(self._view)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._pieces = []
        self._destinations = {}
        self._already_set = []
        self._can_i_talk = True


        #TODO: generalize for the game
        #TODO: do on the game initialization
        # mypath = "//home//robocomp//robocomp//components//euroage-tv//components//tvGames//src//games//draganddropgame//resources//videos"
        # onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]



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
        # self._view.setAttribute(Qt.WA_AcceptTouchEvents)
        # self._view.viewport().setAttribute(Qt.WA_AcceptTouchEvents)



    def init_game(self, config_file_path='resources/game1.json'):
        self.clear_scene()
        self.game_config = None
        self.grabbed = None
        self.correct_images = 0
        self.total_images = 0
        self._pointers = {}
        self._pieces = []
        self._destinations = {}
        # load config game file
        with open(os.path.join(CURRENT_PATH, config_file_path)) as config_file:
            self.game_config = json.load(config_file)
            self.game_config["config_path"] = config_file_path
        self.setWindowState(Qt.WindowMaximized)
        # self.resize(self.game_config["size"][0], self.game_config["size"][1])
        self.create_and_add_images()

        # self.draw_position(self.scene.width()/2, self.scene.height()/2, False)
        # self.clock.set_time(int(self.game_config["time"]))
        # self.clock.set_time(3)
        # self._update_scores()
        # self.clock.show()

        # TODO: Fix it
        # to avoid the resize to the exact escen we create a invisible item at 0,0 in the scene
        # it's beacuse the wai the resizeEvent is implemented
        self._invisible_00_item = QGraphicsRectItem(0,0, 0,0)
        self._scene.addItem(self._invisible_00_item)

        # Calculate the bottom right position
        far_right_piece_pos = [0,0]
        for destination in self._destinations.values():
            if destination.pos().y()+destination.height > far_right_piece_pos[1]:
                far_right_piece_pos = [destination.pos().x()+destination.width, destination.pos().y()+destination.height]
            elif destination.pos().y()+destination.height == far_right_piece_pos[1]:
                if destination.pos().x() > far_right_piece_pos[0]:
                    far_right_piece_pos = [destination.pos().x()+destination.width, destination.pos().y()+destination.height]

        # add invisible item to let the title been seen
        self._invisible_last_item = QGraphicsRectItem(far_right_piece_pos[0]+10, far_right_piece_pos[1]+20, 0, 0)
        self._scene.addItem(self._invisible_last_item)


    def clear_scene(self):
        print("Removing %d destinies"%len(self._destinations))
        for dest in self._destinations.values():
            if dest in self._scene.items():
                self._scene.removeItem(dest)
        print("Removing %d pieces"%len(self._pieces))
        for piece in self._pieces:
            if piece in self._scene.items():
                self._scene.removeItem(piece)
        if self._pointers is not None and len(self._pointers) > 0:
            for pointer in self._pointers.values():
                if pointer in self._scene.items():
                    self.remove_pointer(pointer)
        print("Items yet in scene: ", len(self._scene.items()))
        for item in self._scene.items():
            self._scene.removeItem(item)


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
                print ("TakeDragGame.remove_pointer() : WARNING unknown id " + str(pointer))
                return
        #
        elif isinstance(pointer, Pointer):
            the_pointer = pointer
        else:
            print ("TakeDragGame.remove_pointer() : ERROR unexpected type "+str(type(pointer)))
            return
        if the_pointer.id in self._pointers:
            # print("Removing pointer id %d"%(the_pointer.id))
            the_pointer.stop()
            if the_pointer.open_widget.scene():
                self._scene.removeItem(the_pointer.open_widget)
            if the_pointer.closed_widget.scene():
                self._scene.removeItem(the_pointer.closed_widget)
            del self._pointers[the_pointer.id]

    def show(self):
        self.show_on_second_screen()
        self.clock.start()

    def start(self):
        self.clock.start()

    def game_timeout(self):
        result = self.check_win()
        self.end_game()

    def check_scores(self):
        if self.check_win():
            self.game_win.emit()
        else:
            self._update_scores()

    def _update_scores(self):
        right, wrong = self.right_wrong_pieces()
        self.score_update.emit(right, wrong)

    def end_game(self):
        self.clear_scene()

    def already_set_pieces(self):
        self.right_wrong_pieces()
        set_pieces = []
        # loop over sorted destinations
        for index in range(1, len(self._destinations)+1):
            if self._destinations[index].contained_piece is not None:
                piece = self._destinations[index].contained_piece
                set_pieces.append(piece)
        return set_pieces

    def add_new_pointer(self, pointer_id, xpos, ypos, grab, visible=False):
        # print "TakeDragGame.add_new_pointer: ID=%d"%pointer_id

        open_pointer_widget = self.game_config["images"]["handOpen"]["widget"].clone()
        close_pointer_widget = self.game_config["images"]["handClose"]["widget"].clone()
        open_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
        close_pointer_widget.setZValue(int(self.game_config["depth"]["mouse"]))
        self._pointers[pointer_id] = Pointer(pointer_id, xpos, ypos, grab, open_pointer_widget, close_pointer_widget)
        self._pointers[pointer_id]._lost_timer.timeout.connect(self.remove_pointer)
        if visible:
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
                if len(items) > 0:
                    for item in items:
                        if isinstance(item, QOpencvGraphicsVideoItem):
                            self._pointers[pointer_id].taken = item
                            # Set the Z position of the object take under the pointer Z value
                            self._pointers[pointer_id].taken.setZValue(int(self.game_config["depth"]["mouse"]) - 1)
                            if item.is_playing():
                                item.stop()
                            else:
                                item.play()
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
                self.say_feedback()
                # self._update_scores()

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
                # self._pointers[pointer_id].taken.stop_item()
                self._pointers[pointer_id].taken = None


        # self.game_config["images"]["handOpen"]["widget"].show()
        # self.game_config["images"]["handClose"]["widget"].hide()

    # self.game_config["images"]["handOpen"]["widget"].setPos(new_xpos, new_ypos)
    # self.game_config["images"]["handClose"]["widget"].setPos(new_xpos, new_ypos)


    def adjust_to_nearest_destination(self, pointer_id):
        lowest_distance = sys.maxsize
        nearest_dest = None
        taken_widget = self._pointers[pointer_id].taken
        for dest in self._destinations.values():
            distance = self.items_distance(taken_widget, dest)
            if distance < lowest_distance:
                lowest_distance = distance
                nearest_dest = dest
        print("=======================")
        print("Adjust to nearest destination: index %d at %d for piece %s"%(nearest_dest.index,lowest_distance, taken_widget.id))
        # If the distance to the correct position is less that a configured threshold
        if nearest_dest is not None and lowest_distance < int(self.game_config["difficult"]):
            # Adjust the position of the taken object to the exact correct one
            widths_diff = int((taken_widget.width - dest.width)/2)
            heights_diff = int((taken_widget.height - dest.height) / 2)

            new_xpos = nearest_dest.scenePos().x() - widths_diff
            new_ypos = nearest_dest.scenePos().y() - heights_diff

            piece_added = self.add_piece_to_destination(taken_widget, nearest_dest)
            if piece_added or nearest_dest.contained_piece == taken_widget:
                print("Piece %s added to destination %d"%(taken_widget.id, nearest_dest.index))
                #If added set pos to center
                taken_widget.setPos(new_xpos, new_ypos)
                self._scene.update()

                # TODO: remove If we only want to check win whn Comprobar button is clicked
                # if self.check_win():
                #    self.game_win.emit()
            else:
                print("Piece %s NOT added to destination %s becuase occupied by %s" % (taken_widget.id, nearest_dest.index, nearest_dest.contained_piece.id))
                #If already occupied, set to center but displaced
                rand_x = randint(20,60)
                rand_y = randint(-60, -20)
                taken_widget.setPos(new_xpos+rand_x, new_ypos+rand_y)
        else:
            # If no near destination for this piece
            # and If the dropped piece had a current (previous destination)
            self.remove_piece_from_destination(taken_widget)
        print("=======================")

    def say_feedback(self):
        if self._can_i_talk == False:
            return
        # TODO: Move to a config file or parameter
        talkative_probability = 90
        talkative = randint(1, 99)
        if talkative < talkative_probability:
            text = None
            right, wrong = self.right_wrong_pieces()
            if wrong == 0 and right > 0:
                index = randint(0, len(CONGRAT_STRINGS))
                if index <= len(CONGRAT_STRINGS):
                    text = CONGRAT_STRINGS[index]
            elif wrong > 1 and right == 0:
                index = randint(0, len(RECHECK_STRINGS))
                if index <= len(RECHECK_STRINGS):
                    text = RECHECK_STRINGS[index]
            elif right >= wrong and right > 1:
                index = randint(0, len(RIGHT_STRINGS))
                if index <= len(RIGHT_STRINGS):
                    text = RIGHT_STRINGS[index]
            elif wrong > right and wrong > 1:
                index = randint(0, len(WRONG_STRINGS))
                if index <= len(WRONG_STRINGS):
                    text = WRONG_STRINGS[index]

            if text is not None:
                subprocess.Popen(SPEECH_COMMAND + "\"" + text + "\"", stdout=DEVNULL, shell=True)
                self._can_i_talk = False
                # TODO: This time would be configurable
                QTimer.singleShot(5000, self.feedback_silence_timeout)

    def feedback_silence_timeout(self):
        self._can_i_talk = True


    def add_piece_to_destination(self, piece, destination):
        if destination.empty() or destination.contained_piece == piece:
            #remove piece from it current destination if any
            self.remove_piece_from_destination(piece)
            #update piece and destination
            piece.current_destination = destination
            destination.contained_piece = piece
            return True
        else:
            print("adding failed: ", piece.id, destination.index, destination.contained_piece.id)
            self.remove_piece_from_destination(piece)
            return False

    def remove_piece_from_destination(self, piece=None, destination=None):
        if destination is None:
            if piece.current_destination is not None:
                destination = piece.current_destination
            else:
                print("Trying to remove piece %s from destination without destination"%piece.id)
                return False
        if piece is None:
            if destination.contained_piece is not None:
                piece = destination.contained_piece
            else:
                print("Trying to remove piece from destination (%d) without piece"%destination.index)
                return False
        # remove the piece from the destination
        destination.contained_piece = None
        # remove destination from piece
        piece.current_destination = None
        print("Removed piece %s from destionation index %d"%(piece.id, destination.index))
        return True


    def items_distance(self, item1, item2):
        item1_center_x = item1.scenePos().x() + item1.width / 2.
        item2_center_x = item2.scenePos().x() + item2.width / 2.
        xdistance = item1_center_x - item2_center_x

        item1_center_y = item1.scenePos().y() + item1.height / 2.
        item2_center_y = item2.scenePos().y() + item2.height / 2.
        ydistance = item1_center_y - item2_center_y

        distance = math.sqrt(pow(xdistance, 2) + pow(ydistance, 2))
        return distance

    def create_and_add_images(self):

        if self.game_config is not None:
            temp_pieces_pos = []
            for image_id, item in self.game_config["images"].items():
                config_path = os.path.dirname(self.game_config["config_path"])
                image_path = os.path.join(config_path, item["image_path"])

                if "video_path" in item:
                    clip_path = os.path.join(config_path, item["video_path"])
                    new_image = QOpencvGraphicsVideoItem(image_id, image_path, clip_path, item["title"])
                else:
                    new_image = DraggableItem(image_id, image_path)


                new_image.setZValue(int(self.game_config["depth"][item["category"]]))
                new_image.setPos(item["initial_pose"][0], item["initial_pose"][1])
                # Height is calculate proportional to the width
                new_image.width = item["size"][0]
                self.game_config["images"][image_id]["widget"] = new_image
                if item["category"] != "mouse":
                    self._scene.addItem(new_image)
                if item["category"] == "piece":
                    # used to set random initial position
                    temp_pieces_pos.append((item["initial_pose"][0], item["initial_pose"][1]))
                    dest_item = DestinationItem(new_image.boundingRect(), item["index"])
                    dest_item.setPos(item["final_pose"][0], item["final_pose"][1])
                    new_image.final_destination = dest_item
                    self._pieces.append(new_image)
                    self._destinations[dest_item.index]=dest_item
                    self.total_images = self.total_images + 1
                    self._scene.addItem(dest_item)

            # Randomize initial position
            random.shuffle(temp_pieces_pos)
            for piece in self._pieces:
                random_new_pos = temp_pieces_pos.pop()
                piece.setPos(random_new_pos[0], random_new_pos[1])

            ############# FOR AUTO RESIZING AND POSITIONING PIECES ########
            # self.resize_pieces_auto()
            # self.set_random_initial_auto_pieces_positions()
            # self.set_auto_initial_destinations_positions()


    def resize_pieces_auto(self):
        num_pieces = len(self._pieces)
        piece_margins = 5
        new_piece_width = (self._scene.sceneRect().width()-(piece_margins*2*num_pieces))/num_pieces
        for piece in self._pieces:
            piece.width = new_piece_width

    def calculate_initial_auto_pieces_positions(self):
        piece_margins = 5
        last_pos_x = 0
        pieces_positions = []
        # We divide the heght in 5 "lines" and the pieces goes on the second one
        new_pos_y = self._scene.sceneRect().height()/5

        for piece in self._pieces:
            new_pos_x = last_pos_x + piece_margins
            last_pos_x = new_pos_x + piece.width + piece_margins
            pieces_positions.append((new_pos_x, new_pos_y))
        return pieces_positions

    def set_random_initial_auto_pieces_positions(self, random_order=True):
        initial_pos = self.calculate_initial_auto_pieces_positions()
        if random_order:
            random.shuffle(initial_pos)
        for piece in self._pieces:
            random_new_pos = initial_pos.pop()
            if piece.initial_pos is None:
                self.initial_pos = random_new_pos
                piece.setPos(random_new_pos[0], random_new_pos[1])

    def set_auto_initial_destinations_positions(self):
        initial_positions = self.calculate_initial_auto_pieces_positions()
        for i in range(len(self._destinations)):
            self._destinations[i].setPos(initial_positions(i))

    def check_win(self):
        right, wrong = self.right_wrong_pieces()
        if right == len(self._pieces):
            return True

    def check_lose(self):
        right, wrong = self.right_wrong_pieces()
        if wrong > 0:
            return True

    def right_wrong_pieces(self):
        right = 0
        wrong = 0
        self._already_set = []
        for destination in self._destinations.values():
            if destination.contained_piece is not None:
                if destination.contained_piece.final_destination == destination:
                    right+=1
                else:
                    wrong+=1
        return right, wrong

    def adjust_view(self):
        self._view.fitInView(self._scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self._scene.setSceneRect(self._scene.itemsBoundingRect())

    def resizeEvent(self, event):
        # skip initial entry
        self.adjust_view()
        # if self.game_config is not None:
            # self.set_random_initial_auto_pieces_positions()
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
    game = GameScreen(None, 1920, 1080)
    # game.init_game("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/resources/LionKingGame/game.json")
    # game.init_game("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/resources/CALENTAR VASO LECHE/calentar_leche.json")
    game.init_game("/home/robolab/robocomp/components/euroage-tv/components/tvGames/src/games/resources/CALENTAR VASO LECHE/calentar_leche.json")
    game.show_on_second_screen()

    # main_widget = GameWidget()
    # main_widget.show_on_second_screen()
    # window = TakeDragGame(1920, 1080)
    # window.show()



    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
