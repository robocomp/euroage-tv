# -*- coding: utf-8 -*-
"""The user interface for our app"""
import json
import os
import sys
import time
from random import randint, shuffle

from OpenGL import GL
# Create a class for our main window
from PyQt4.QtCore import Qt, QTimer, QTimeLine, QPointF, pyqtSignal, QObject
from PyQt4.QtGui import QApplication, QGraphicsItemAnimation, QGraphicsTextItem, QFont, QGraphicsScene, QHBoxLayout, \
    QWidget, QGraphicsView, QPixmap, QGraphicsPixmapItem, QBrush, QGraphicsItem, QStyleOptionGraphicsItem, \
    QGraphicsRectItem, QStyle
from PyQt4 import QtOpenGL

# Images got from public domain Pixabay  site
# https://pixabay.com/en/shorts-beach-clothing-summer-149409/
# https://pixabay.com/en/polo-shirt-t-shirt-clothes-shirt-154158/
# https://pixabay.com/en/jacket-winter-clothing-cold-wear-32714/
# https://pixabay.com/en/clothes-clothing-hose-trousers-1294974/
# https://pixabay.com/en/cupboard-wooden-storage-cabinet-575356/
# https://pixabay.com/en/crate-wood-box-archive-1143427/

CURRENT_PATH = os.path.dirname(__file__)


class MovedSignal(QObject):
    moved = pyqtSignal(QPointF)

    def __init__(self, parent=None):
        self.parent = parent
        super(MovedSignal, self).__init__()

    def get_parent(self):
        return self.parent

class DraggableItem(QGraphicsPixmapItem):

    def __init__(self, image_path, parent=None):
        super(DraggableItem, self).__init__(parent)
        self.pixmap = QPixmap(image_path)
        self.pixmap = self.pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.moved_flag = False
        self.old_pos = None
        self.moved_signal = MovedSignal(self)


    #
    # def itemChange(self, change, value):
    #     if change == QGraphicsItem.ItemPositionChange:
    #         self.moved = True
    #     return super(DraggableItem, self).itemChange(change,value)

    def paint(self, painter, option, widget):
        myOption = QStyleOptionGraphicsItem(option)
        if option.state & QStyle.State_Selected:
            myOption.state = myOption.state ^ QStyle.State_Selected
        super(DraggableItem, self).paint(painter, myOption, widget)

    # We must override these or else the default implementation prevents
    #  the mouseMoveEvent() override from working.
    def mousePressEvent(self, event):
        self.old_pos = event.scenePos()
        super(DraggableItem, self).mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if self.old_pos:
            point = event.scenePos() - self.old_pos
            if point.manhattanLength() > 3:
                self.moved_flag = True
                self.moved_signal.moved.emit(event.scenePos())
        super(DraggableItem, self).mouseReleaseEvent(event)


class TakeDragGame(QWidget):
    def __init__(self, parent=None):
        super(TakeDragGame, self).__init__(parent)

        # This is always the same
        self.dot2 = QGraphicsTextItem(':')
        self.dot1 = QGraphicsTextItem(':')
        self.animations = []
        self.digits = []
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 400)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        # TODO: Check if its better with opengl or not
        # self.view.setViewport(QtOpenGL.QGLWidget())
        self.main_layout.addWidget(self.view)
        self.setWindowState(Qt.WindowMaximized)
        self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.image_bank = None
        self.create_and_add_images()

        # self.scene.setBackgroundBrush(QBrush(Qt.red, Qt.SolidPattern))

        # self.populate()
        # self.animator = QTimer()
        # self.animator.timeout.connect(self.animate)
        # self.animate()

    def create_and_add_images(self):
        self.load_images_json_file()
        self.add_background_to_image()
        self.add_background_from_image()
        if self.image_bank is not None:
            for image_id in self.image_bank.keys():
                if "clothes" in self.image_bank[image_id]["categories"]:
                    image_path = self.image_bank[image_id]["path"]
                    new_image = DraggableItem(image_path, self.background_from_image)
                    new_image.moved_signal.moved.connect(self.item_moved)
                    self.image_bank[image_id]["widget"] = new_image
                    newpos_x = self.background_from_image.boundingRect().width() / 2 - new_image.boundingRect().width() / 2
                    newpos_y = self.background_from_image.boundingRect().height() / 2 - new_image.boundingRect().height() / 2
                    new_image.setPos(newpos_x, newpos_y)
                    # self.scene.addItem(new_image)
                    new_image.setZValue(30)

    def item_moved(self, pos):
        widget = self.sender().get_parent()
        print widget.zValue()
        print self.background_from_image.zValue()
        print self.background_to_image.zValue()
        item_br = widget.sceneBoundingRect()
        if self.background_from_image.sceneBoundingRect().contains(item_br):
            widget.setParentItem(self.background_from_image)
            newpos_x = self.background_from_image.boundingRect().width() / 2 - widget.boundingRect().width() / 2
            newpos_y = self.background_from_image.boundingRect().height() / 2 - widget.boundingRect().height() / 2
            # self.background_to_image.stackBefore(self.background_from_image)
            widget.setPos(newpos_x, newpos_y)
        elif self.background_to_image.sceneBoundingRect().contains(item_br):
            widget.setParentItem(self.background_to_image)
            newpos_x = self.background_to_image.boundingRect().width() / 2 - widget.boundingRect().width() / 2
            newpos_y = self.background_to_image.boundingRect().height() / 2 - widget.boundingRect().height() / 2
            # self.background_from_image.stackBefore(self.background_to_image)
            widget.setPos(newpos_x, newpos_y)



    def load_images_json_file(self):
        with open(os.path.join(CURRENT_PATH, './resources/images.json')) as f:
            self.image_bank = json.load(f)

    def add_background_from_image(self, ):
        assert self.image_bank is not None, "Images need to be loaded before calling this method (try load_images_json_file)"
        if "Background from" in self.image_bank:
            background_from_pixmap = QPixmap(self.image_bank["Background from"]["path"])
            self.background_from_image = QGraphicsPixmapItem(background_from_pixmap)
            self.scene.addItem(self.background_from_image)
            self.background_from_image.setZValue(2)

    def add_background_to_image(self, ):
        assert self.image_bank is not None, "Images need to be loaded before calling this method (try load_images_json_file)"
        if "Background to" in self.image_bank:
            background_to_pixmap = QPixmap(self.image_bank["Background to"]["path"])
            self.background_to_image = QGraphicsPixmapItem(background_to_pixmap)
            self.scene.addItem(self.background_to_image)
            self.background_to_image.setZValue(2)

    def resizeEvent(self, event):
        view_size = self.view.size()
        new_background_height = (1.5 / 4.) * view_size.height()
        background_to_pixmap = QPixmap(self.image_bank["Background to"]["path"])
        background_to_pixmap = background_to_pixmap.scaled(new_background_height, new_background_height,
                                                           Qt.KeepAspectRatio)
        if not self.background_to_image:
            self.background_to_image = QGraphicsPixmapItem(background_to_pixmap)
        else:
            self.background_to_image.setPixmap(background_to_pixmap)
        sugested_x_position = int(2 * (view_size.width() / 3.))
        if sugested_x_position < 0:
            sugested_x_position = 0
        sugested_y_position = int(view_size.height() / 2. - background_to_pixmap.size().height() / 2)
        if sugested_y_position < 0:
            sugested_y_position = 0
        self.background_to_image.setPos(sugested_x_position, sugested_y_position)

        #####################
        new_background_height = (2.2 / 4.) * view_size.height()
        background_from_pixmap = QPixmap(self.image_bank["Background from"]["path"])
        background_from_pixmap = background_from_pixmap.scaled(new_background_height, new_background_height,
                                                               Qt.KeepAspectRatio)
        if not self.background_to_image:
            self.background_from_image = QGraphicsPixmapItem(background_from_pixmap)
        else:
            self.background_from_image.setPixmap(background_from_pixmap)

        sugested_x_position = int(view_size.width() / 5. - background_from_pixmap.size().height() / 2)
        if sugested_x_position < 0:
            sugested_x_position = 0
        sugested_y_position = int(view_size.height() / 2. - background_from_pixmap.size().height() / 2)
        if sugested_y_position < 0:
            sugested_y_position = 0
        self.background_from_image.setPos(sugested_x_position, sugested_y_position)

        ####
        new_widget_height = (1 / 4.) * view_size.height()
        if self.image_bank is not None:
            for image_id in self.image_bank.keys():
                if "clothes" in self.image_bank[image_id]["categories"]:
                    widget = self.image_bank[image_id]["widget"]
                    pixmap = widget.pixmap
                    pixmap = pixmap.scaled(new_widget_height, new_widget_height,
                                           Qt.KeepAspectRatio)
                    widget.setPixmap(pixmap)
                    print widget.moved_flag
                    if not widget.moved_flag:
                        newpos_x = self.background_from_image.boundingRect().width() / 2 - widget.boundingRect().width() / 2
                        newpos_y = self.background_from_image.boundingRect().height() / 2 - widget.boundingRect().height() / 2
                        widget.setPos(newpos_x, newpos_y)

        super(TakeDragGame, self).resizeEvent(event)


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
