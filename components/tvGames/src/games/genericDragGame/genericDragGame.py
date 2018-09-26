# -*- coding: utf-8 -*-
"""The user interface for our app"""
import json
import math
import os
import sys

# Create a class for our main window
from PyQt4.QtCore import Qt, QTimer, QPointF, pyqtSignal, QDateTime
from PyQt4.QtGui import QApplication, QGraphicsScene, QHBoxLayout, \
    QWidget, QGraphicsView, QPixmap, QGraphicsPixmapItem, QLabel, QFont, QPainter, QImage

CURRENT_PATH = os.path.dirname(__file__)


class MyQGraphicsScene(QGraphicsScene):
    moved = pyqtSignal(int, int, bool)

    def mousePressEvent(self, event):
        self.moved.emit(event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

    def mouseMoveEvent(self, event):
        self.moved.emit(event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)

    def mouseReleaseEvent(self, event):
        self.moved.emit(event.scenePos().x(), event.scenePos().y(), event.buttons() == Qt.LeftButton)


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
        aux_image = QImage("./resources/check-mark.png").scaled(self.width / 2, self.height / 2, Qt.KeepAspectRatio)
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



class TakeDragGame(QWidget):
    def __init__(self, width=800, height=800, parent=None):
        super(TakeDragGame, self).__init__(parent)
        # ui
        self.width = width
        self.height = height
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.scene = MyQGraphicsScene()
#DISCONNECT MOUSE
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
#        self.setWindowState(Qt.WindowMaximized)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.clock = QLabel("00:00")
        self.clock.hide()
        self.clock.setAttribute(Qt.WA_TranslucentBackground)
        self.clock.setFont(QFont("Arial", 70, QFont.Bold))
        self.clock.move(self.width - self.clock.size().width(), 0)
        self.scene.addWidget(self.clock)
        self.endMessage = QLabel(u"¡Has perdido!")
        self.endMessage.hide()
        self.endMessage.setAttribute(Qt.WA_TranslucentBackground)
        self.endMessage.setFont(QFont("Arial", 90, QFont.Bold))
        self.endMessage.move(self.width / 2 - self.endMessage.size().width() / 2,
                             self.height / 2 - self.endMessage.size().height() / 2)
        self.scene.addWidget(self.endMessage)
        # game data
        self.total_images = 0
        self.correct_images = 0
        self.time = None
        self.scene.setSceneRect(0, 0, width, height)
        self.grabbed = None
        self.game_config = None
        self.config = ""
        self.init_game('./resources/game1.json')


    def init_game(self, config_file):
        self.game_config = None
        self.grabbed = None
        self.correct_images = 0
        self.total_images = 0
        # load config game file
        with open(os.path.join(CURRENT_PATH, config_file)) as file_path:
            self.game_config = json.load(file_path)
        self.create_and_add_images()
        self.draw_position(self.scene.width()/2, self.scene.height()/2, False)
        self.time = int(self.game_config["time"])
        self.endMessage.hide()
        self.clock.show()
        self.update_clock()
        self.timer.start(1000)


    def end_game(self, value):
        self.timer.stop()
        if value:
            self.endMessage.setText(u"<font color='green'>¡Has ganado!</font>")
        else:
            self.endMessage.setText(u"<font color='red'>¡Has perdido!</font>")
        self.endMessage.show()
        self.clock.hide()


    def update_clock(self):
        time_string = QDateTime.fromTime_t(self.time).toString("mm:ss")
        self.clock.setText(time_string)
        if self.time <= 0:
            self.end_game(False)
        self.time = self.time - 1


    def update_pointer(self, xpos, ypos, grab):
        self.draw_position(xpos, ypos, grab)
        if grab:
            if self.grabbed:
                new_xpos = xpos - self.grabbed.boundingRect().width() / 2
                new_ypos = ypos - self.grabbed.boundingRect().height() / 2
                self.grabbed.setPos(new_xpos, new_ypos)
            else:
                items = self.scene.items(QPointF(xpos, ypos))
                if len(items) > 1:
                    if items[1].draggable:
                        self.grabbed = items[1]
                        items[1].setZValue(int(self.game_config["depth"]["mouse"]) - 1)
        else:
            if self.grabbed:
                # adjust Z value
                items = self.scene.items(QPointF(xpos, ypos))
                zvalue = int(self.game_config["depth"]["image"])
                if len(items) > 1:
                    zvalue = zvalue + len(items) * 2
                self.grabbed.setZValue(zvalue)
                # check correct position
                xdistance = (self.grabbed.scenePos().x() + self.grabbed.width / 2) - self.grabbed.final_posex
                ydistance = (self.grabbed.scenePos().y() + self.grabbed.height / 2) - self.grabbed.final_posey
                distance = math.sqrt(pow(xdistance, 2) + pow(ydistance, 2))
                print distance
                if distance < int(self.game_config["difficult"]):
                    print "Correct position"
                    new_xpos = self.grabbed.final_posex - self.grabbed.width / 2
                    new_ypos = self.grabbed.final_posey - self.grabbed.height / 2
                    self.grabbed.setPos(new_xpos, new_ypos)
                    self.grabbed.set_overlay(True)
                    if not self.grabbed.correct_position:
                        self.grabbed.correct_position = True
                        self.correct_images = self.correct_images + 1
                    if self.correct_images == self.total_images:
                        self.end_game(True)
                else:
                    if self.grabbed.correct_position:
                        self.grabbed.correct_position = False
                        self.correct_images = self.correct_images - 1
                    self.grabbed.set_overlay(False)
                self.grabbed = None


    def draw_position(self, xpos, ypos, grab):
        if grab:
            self.game_config["images"]["handOpen"]["widget"].hide()
            self.game_config["images"]["handClose"]["widget"].show()
        else:
            self.game_config["images"]["handOpen"]["widget"].show()
            self.game_config["images"]["handClose"]["widget"].hide()
        new_xpos = xpos - self.game_config["images"]["handOpen"]["widget"].boundingRect().width() / 2
        new_ypos = ypos - self.game_config["images"]["handOpen"]["widget"].boundingRect().height() / 2
        self.game_config["images"]["handOpen"]["widget"].setPos(new_xpos, new_ypos)
        self.game_config["images"]["handClose"]["widget"].setPos(new_xpos, new_ypos)


    def create_and_add_images(self):
        if self.game_config is not None:
            for image_id, item in self.game_config["images"].items():
                image_path = os.path.join(CURRENT_PATH, item["path"])
                new_image = DraggableItem(image_id, image_path, item["size"][0], item["size"][1], item["category"] == "image")
                new_image.setPos(item["initial_pose"][0], item["initial_pose"][1])
                new_image.setZValue(int(self.game_config["depth"][item["category"]]))
                self.game_config["images"][image_id]["widget"] = new_image
                self.scene.addItem(new_image)
                if item["category"] == "image":
                    new_image.set_final_pose(item["final_pose"][0], item["final_pose"][1])
                    self.total_images = self.total_images + 1

    def resizeEvent(self, event):
        # skip initial entry
        if event.oldSize().width() < 0 or event.oldSize().height() < 0:
            return
        super(TakeDragGame, self).resizeEvent(event)
        self.clock.move(self.view.width() - self.clock.size().width() * 1.1, 0)
        self.endMessage.move(self.view.width() / 2 - self.endMessage.size().width() / 2,
                             self.view.height() / 2 - self.endMessage.size().height() / 2)
        # images
        xfactor = float(event.size().width()) / float(event.oldSize().width())
        yfactor = float(event.size().height()) / float(event.oldSize().height())
        for key, item in self.game_config["images"].items():
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


def main():
    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QApplication(sys.argv)
    window = TakeDragGame()
    window.show()

    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
