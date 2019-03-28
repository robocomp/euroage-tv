import errno
import os
import sys
from collections import OrderedDict
from os import listdir
from os.path import isfile, join

from PySide2.QtCore import QUrl, Qt, QSize
from PySide2.QtGui import QColor
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import QVBoxLayout, QFrame, QWidget, QApplication, QPushButton, \
    QGraphicsDropShadowEffect, QHBoxLayout

# Python 2 only
if sys.version_info < (3, 0):
    from ptyprocess.ptyprocess import FileNotFoundError


class FrameButton(QPushButton):
    def __init__(self, text="", text_size=10, h=150, w=250, offset=20, color="green", style=None, parent=None):
        self.parent = parent
        super(FrameButton, self).__init__(text, parent)
        self._size = str(h) + "x" + str(w)
        self._offset = offset
        self.setFixedSize(QSize(int(w), int(h)))
        self.set_color(QColor(color), text_size)
        if style:
            self.setStyleSheet(style)
        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

        # Shadow
        self._set_released_shadow()

    def set_color(self, color, text_size):
        if isinstance(color, QColor):
            self.setStyleSheet(
                "QPushButton{border-radius:15px; border:2px solid #000000; color:#ffffff; font-size:" + str(
                    text_size) + "px; font-weight:bold; padding:16px 31px; } QPushButton:hover {background-color: " + color.name() + ";} QPushButton:!hover { background-color:" + color.darker(
                    150).name() + ";  }")
            self.update()
        else:
            raise Exception("color must be a QColor class")

    def _set_pressed_shadow(self):
        pressed_shadow = QGraphicsDropShadowEffect(self)
        pressed_shadow.setBlurRadius(10)
        pressed_shadow.setOffset(2)
        self.setGraphicsEffect(pressed_shadow)
        self.update()

    def _set_released_shadow(self):
        released_shadow = QGraphicsDropShadowEffect(self)
        released_shadow.setBlurRadius(22)
        released_shadow.setOffset(10)
        self.setGraphicsEffect(released_shadow)
        self.update()

    def _button_pressed(self):
        self.w, self.h = self.width() - self._offset, self.height() - self._offset
        self.offset = self._offset / 2
        self._set_pressed_shadow()

    def _button_released(self):
        self._set_released_shadow()


class ListVideoPlayer(QWidget):
    def __init__(self, relative_width=0.8, relative_height=0.8, parent=None):
        super(ListVideoPlayer, self).__init__(parent=parent)
        self._frame = QFrame()

        self._video_widget = QVideoWidget(self._frame)
        self._current_play_list = QMediaPlaylist()
        self._media_player = QMediaPlayer(self)
        self._media_player.setVideoOutput(self._video_widget)
        self._media_player.setPlaylist(self._current_play_list)

        self._frame_layout = QVBoxLayout()
        self._button_layout = QHBoxLayout()

        self._frame.setLayout(self._frame_layout)
        self._frame.setLayout(self._button_layout)
        self._frame_layout.addWidget(self._video_widget)

        self._full_media_list = []

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._frame, 1)

        self.play_button = FrameButton(text="PAUSAR", text_size=30, color="#3cc21b", parent=self)
        self.stop_button = FrameButton(text="CERRAR", text_size=30, color="#c21b1b", parent=self)
        self._button_layout.addWidget(self.play_button)
        self._button_layout.addWidget(self.stop_button)

        self._main_layout.addLayout(self._button_layout)
        self._main_layout.setAlignment(self.play_button, Qt.AlignCenter)
        self._main_layout.setContentsMargins(4, 4, 4, 8)
        self._frame_layout.setContentsMargins(0, 0, 0, 4)

        self._frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setLayout(self._main_layout)

        desktop_widget = QApplication.desktop().screenGeometry(0)
        self.setFixedSize(desktop_widget.width() * relative_width, desktop_widget.height() * relative_height)
        self.setMaximumSize(desktop_widget.width() * relative_width, desktop_widget.height() * relative_height)
        self.move(desktop_widget.width() * (1 - relative_width) / 2,
                  desktop_widget.height() * (1 - relative_height) / 2)

        # self._played_videos = 0
        # # self.audio.setVolume(50)
        self._media_player.stateChanged.connect(self.handle_state_changed)
        # self._reproduce_multiple = False

    def handle_state_changed(self, newstate):
        print(newstate)

    def add_path_to_video_list(self, video_path):
        if os.path.exists(video_path):
            self._full_media_list.append(video_path)
            return len(self._full_media_list) - 1
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), video_path)
            return -1

    def play_indexes_list(self, video_indexes):
        self._current_play_list.clear()
        for index in video_indexes:
            if index in range(len(self._full_media_list)):
                path = self._full_media_list[index]
                self._current_play_list.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self._media_player.play()

    def reproduce_all(self):
        self._current_play_list.addMedia(self._full_media_list)

    def clear(self):
        self._current_play_list.clear()


class ActionsVideoPlayer(ListVideoPlayer):
    def __init__(self, relative_width=0.8, relative_height=0.8, parent=None):
        super(ActionsVideoPlayer, self).__init__(relative_width, relative_height, parent)
        self._actions_list = OrderedDict()

        self._index_to_key = {}  # index from index number of actions to action keys (names)
        self._index_to_playlist = {}
        self._currently_playing = []

        # self.setWindowFlags(
        #     Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # TODO: Only needed because the problem with QVideoWidget and QGraphicScene
        self.play_button.clicked.connect(self._play_pause)
        self.stop_button.clicked.connect(self._stop)

    def add_action(self, action_key, clip_path, action_index=None):
        if action_index is None:
            next_index = len(self._actions_list)
        else:
            if action_index not in self._index_to_key.keys():
                next_index = action_index
            else:
                raise IndexError("Trying to use already existing index %d for action '%s'" % (action_index, action_key))

        self._actions_list[action_key] = {"index": next_index, "clip_path": clip_path}  # save the action name by index
        self._index_to_key[next_index] = action_key  # save the index in the playlist
        self._index_to_playlist[action_key] = self.add_path_to_video_list(clip_path)

    def set_video_list(self, path, format=".mp4"):
        files = {f[:-4]: f for f in listdir(path) if isfile(join(path, f)) and f.upper().endswith(format.upper())}
        try:
            for k in sorted(files):
                self.add_action(k, path + files[k])
        except Exception as e:
            print(str(e))



    def play_all_actions(self):
        self.play_indexes_list(self._index_to_playlist.values())

    def play_one_action(self, action_key):
        play_list_index = self._index_to_playlist[action_key]
        if [play_list_index] != self._currently_playing or self._media_player.state() != QMediaPlayer.PlayingState:
            self.play_indexes_list([play_list_index])
            self._currently_playing = [play_list_index]

    def _play_pause(self):
        if self._media_player.state() == QMediaPlayer.PlayingState:
            self._media_player.pause()
        else:
            self._media_player.play()

    def _stop(self):
        self._media_player.stop()
        self._current_play_list.clear()
        self._close()

    def _close(self):
        self.hide()

    def show_on_second_screen(self):
        desktop_widget = QApplication.desktop()
        if desktop_widget.screenCount() > 1:
            # TODO: set 1 to production
            second_screen_size = desktop_widget.screenGeometry(1)
            newx = second_screen_size.left() + (second_screen_size.width()-self.width())/2
            newy = second_screen_size.top() + (second_screen_size.height() - self.height()) / 2
            self.move(newx, newy)
            # self.resize(second_screen_size.width(), second_screen_size.height())
            self.showFullScreen()

    def clear(self):
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []
        super(ActionsVideoPlayer, self).clear()

    def __contains__(self, key):
        return key in self._actions_list.keys()


# def newTest(path, index=None):
#     print("New test: ", index)
#     window = ActionsVideoPlayer(0.55, 0.71)
#     print(path)
#     window.add_action()
#     window.set_video_list(path)
#     if index is not None:
#         window.play_indexes_list([index])
#     else:
#         window.play_all_actions()
#     window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    path = "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/final_game1/videos/"
    window = ActionsVideoPlayer(0.55, 0.71)
    window.set_video_list(path)
    window.play_all_actions()
    # window.setFixedSize(200,240)
    window.show()

    # for i in range(0, 5):
    #     newTest(path, i)

    sys.exit(app.exec_())
