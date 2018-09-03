import json
import os
import sys
from PyQt4 import QtGui
from math import floor, sqrt
from pprint import pprint
from random import shuffle, randint

import cv2
import numpy as np
from PyQt4.QtCore import pyqtSignal, Qt, QTimer
from PyQt4.QtGui import QWidget, QApplication, QPixmap, QGridLayout, QLabel, QImage

CURRENT_PATH = os.path.dirname(__file__)


def blend_transparent(face_img, overlay_t_img):
    new_overlay_image = np.zeros(face_img.shape, dtype=np.uint8)
    face_img = face_img[:, :, :3]
    x_of_overlay = int(face_img.shape[1] / 2. - overlay_t_img.shape[1] / 2)
    y_of_overlay = int(face_img.shape[0] / 2. - overlay_t_img.shape[0] / 2)
    new_overlay_image[y_of_overlay:y_of_overlay + overlay_t_img.shape[0],
    x_of_overlay:x_of_overlay + overlay_t_img.shape[1]] = overlay_t_img

    # Split out the transparency mask from the colour info
    overlay_img = new_overlay_image[:, :, :3]  # Grab the BRG planes
    overlay_mask = new_overlay_image[:, :, 3:]  # And the alpha plane

    # Again calculate the inverse mask
    background_mask = 255 - overlay_mask

    # Turn the masks into three channel, so we can use them as weights
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

    # Create a masked out face image, and masked out overlay
    # We convert the images to floating point in range 0.0 - 1.0
    face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

    # And finally just add them together, and rescale it back to an 8bit integer image
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


class ClickableImage(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, image_path, name=None):
        super(ClickableImage, self).__init__()
        self.pixmap = QPixmap(image_path)
        self.path = image_path
        if name is None:
            base = os.path.basename(image_path)
            if len(os.path.splitext(base)) > 1:
                self.name = os.path.splitext(base)[0]
            # TODO: Throw exception
        else:
            self.name = name
        self.setPixmap(self.pixmap)
        self.setObjectName(self.name)
        self.reset_timer = QTimer()
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset_default_image)

    def set_temp_opencv_image(self, image, delay):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], \
                       image.shape[0], image.shape[1] * 3,
                       QImage.Format_RGB888)
        pixmap = QPixmap(image)
        self.setPixmap(pixmap)
        self.reset_timer.start(delay)

    def reset_default_image(self):
        self.setPixmap(self.pixmap)

    # def to_opencv_image(self, share_memory=False):
    #     """ Creates a numpy array from a QImage.
    #
    #         If share_memory is True, the numpy array and the QImage is shared.
    #         Be careful: make sure the numpy array is destroyed before the image,
    #         otherwise the array will point to unreserved memory!!
    #     """
    #     img = self.pixmap.toImage()
    #     assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"
    #     assert img.format() == QtGui.QImage.Format_RGB32, \
    #         "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())
    #
    #     img_size = img.size()
    #     buffer = img.bits()
    #
    #     # Sanity check
    #     n_bits_buffer = len(buffer) * 8
    #     n_bits_image = img_size.width() * img_size.height() * img.depth()
    #     assert n_bits_buffer == n_bits_image, \
    #         "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image)
    #
    #     assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())
    #
    #     # Note the different width height parameter order!
    #     arr = np.ndarray(shape=(img_size.height(), img_size.width(), img.depth() // 8),
    #                      buffer=buffer,
    #                      dtype=np.uint8)
    #
    #     if share_memory:
    #         return arr
    #     else:
    #         return copy.deepcopy(arr)

    def to_opencv_image(self):
        image = self.pixmap.toImage()
        new_image = image.convertToFormat(QtGui.QImage.Format_RGB32)

        width = image.width()
        height = image.height()
        depth = image.depth() // 8

        ptr = new_image.bits()
        s = ptr.asstring(width * height * image.depth() // 8)
        arr = np.fromstring(s, dtype=np.uint8).reshape((height, width, depth))

        return arr

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)


class ChooseImageGame(QWidget):

    def __init__(self, parent=None):
        super(ChooseImageGame, self).__init__(parent)
        self.main_layout = QGridLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.image_grid = []
        self.image_grid_by_name = {}
        self.image_grid_by_widget = {}
        self.win_sign_path = os.path.join(CURRENT_PATH, 'resources/ok_sign.png')
        self.lose_sign_path = os.path.join(CURRENT_PATH, 'resources/wrong_sign.png')
        self.WIN_LOSE_DELAY_TIME = 2 * 1000
        self.current_winner_image = None
        self.restart_game_timer = QTimer()
        self.restart_game_timer.setSingleShot(True)
        self.restart_game_timer.timeout.connect(self.restart_image_tile)
        self.image_bank = {}

    def generate_image_tile_widget_from_paths(self, images_path_list):
        if images_path_list is not None:
            image_count = len(images_path_list)
            rows = int(floor(sqrt(image_count)))
            # columns = int(image_count / rows)
            shuffle(images_path_list)
            for n_image, image_path in enumerate(images_path_list):
                assert os.path.exists(image_path), "%s image path doesn't exist" % image_path
                row = n_image % rows
                column = int(n_image / rows)
                label = ClickableImage(image_path)
                label.clicked.connect(self.handleLabelClicked)
                self.main_layout.addWidget(label, row, column)
                if row < len(self.image_grid):
                    self.image_grid[row].append({"name": label.name, "path": label.path, "widget": label})
                else:
                    col_0 = [{"name": label.name, "path": label.path, "widget": label}]
                    self.image_grid.append(col_0)
                self.image_grid_by_widget[label] = (row, column)
                self.image_grid_by_name[label.name] = (row, column)

    def genera_image_tile_widget(self):
        if self.image_bank is not None or len(self.image_bank)<=0:
            image_count = len(self.image_bank)
            rows = int(floor(sqrt(image_count)))
            # columns = int(image_count / rows)
            image_ids = self.image_bank.keys()
            shuffle(image_ids)
            for n_image, image_id in enumerate(image_ids):
                row = n_image % rows
                column = int(n_image / rows)
                image = self.image_bank[image_id]
                assert os.path.exists(image["path"]), "%s image path doesn't exist" % image["path"]
                label = ClickableImage(image["path"],image["name"])
                label.clicked.connect(self.handleLabelClicked)
                self.main_layout.addWidget(label, row, column)
                if row < len(self.image_grid):
                    self.image_grid[row].append({"name": label.name, "path": label.path, "widget": label})
                else:
                    col_0 = [{"name": label.name, "path": label.path, "widget": label}]
                    self.image_grid.append(col_0)
                self.image_grid_by_widget[label] = (row, column)
                self.image_grid_by_name[label.name] = (row, column)

    def restart_image_tile(self):
        self.image_grid = []
        self.image_grid_by_name = {}
        self.image_grid_by_widget = {}
        self.generate_image_tile_widget_from_paths(
            [os.path.join(CURRENT_PATH, 'resources/1.jpg'),
             os.path.join(CURRENT_PATH, 'resources/2.jpg'),
             os.path.join(CURRENT_PATH, 'resources/3.jpg'),
             os.path.join(CURRENT_PATH, 'resources/4.jpg')]
        )
        self.set_winner_image_by_name(str(randint(1, 4)))

    def set_winner_image_by_name(self, name):
        image_grid_coords = self.image_grid_by_name[str(name)]
        self.current_winner_image = self.image_grid[image_grid_coords[0]][image_grid_coords[1]]["widget"]

    def set_winner_image(self, widget):
        self.current_winner_image = widget

    def handleLabelClicked(self, name):
        image_grid_coords = self.image_grid_by_name[str(name)]
        clicked_widget = self.image_grid[image_grid_coords[0]][image_grid_coords[1]]["widget"]

        if name == self.current_winner_image.name:
            self.overlay_image_win(clicked_widget)
            self.restart_game_timer.start((self.WIN_LOSE_DELAY_TIME / 1000 + 0.5) * 1000)
        else:
            self.overlay_image_lose(clicked_widget)

    def overlay_image_win(self, widget):
        assert os.path.exists(self.win_sign_path), "Lose sign file not found at %s" % self.win_sign_path
        original_image = widget.to_opencv_image()
        win_imag = cv2.imread(self.win_sign_path, cv2.IMREAD_UNCHANGED)
        min_side = min([original_image.shape[0], original_image.shape[1]])
        proportion = float(min_side) / win_imag.shape[0]
        win_imag = cv2.resize(win_imag, None, fx=proportion, fy=proportion, interpolation=cv2.INTER_CUBIC)
        mixed = blend_transparent(original_image, win_imag)
        widget.set_temp_opencv_image(mixed, self.WIN_LOSE_DELAY_TIME)

    def overlay_image_lose(self, widget):
        assert os.path.exists(self.lose_sign_path), "Lose sign file not found at %s" % self.lose_sign_path
        original_image = widget.to_opencv_image()
        lose_image = cv2.imread(self.lose_sign_path, cv2.IMREAD_UNCHANGED)
        min_side = min([original_image.shape[0], original_image.shape[1]])
        proportion = float(min_side) / lose_image.shape[0]
        lose_image = cv2.resize(lose_image, None, fx=proportion, fy=proportion, interpolation=cv2.INTER_CUBIC)
        mixed = blend_transparent(original_image, lose_image)
        widget.set_temp_opencv_image(mixed, self.WIN_LOSE_DELAY_TIME)

    def load_images_json_file(self):
        with open(os.path.join(CURRENT_PATH, 'resources/images.json')) as f:
            self.image_bank = json.load(f)


def main():
    app = QApplication([])
    game = ChooseImageGame()
    game.load_images_json_file()
    game.restart_image_tile()
    game.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
