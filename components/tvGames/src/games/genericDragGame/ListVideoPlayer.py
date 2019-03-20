import errno
import sys
import os

from os import listdir, PathLike
from os.path import isfile, join

from collections import OrderedDict
from time import sleep

from PySide2.QtCore import QUrl, Qt, QSize
from PySide2.QtGui import QColor
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import QVBoxLayout, QFrame, QWidget, QApplication, QLabel, QPushButton, \
    QGraphicsDropShadowEffect, QHBoxLayout

# Python 2 only
if sys.version_info < (3, 0):
    from ptyprocess.ptyprocess import FileNotFoundError


class FrameButton(QPushButton):
    def __init__(self, text="", text_size=10, h=150, w=250, offset=20, color="green", parent=None, style=None):
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
                "QPushButton{border-radius:15px; border:2px solid #000000; color:#ffffff; font-size:" + str(text_size) + "px; font-weight:bold; padding:16px 31px; } QPushButton:hover {background-color: " + color.name() + ";} QPushButton:!hover { background-color:" + color.darker(
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


class PlayButton(FrameButton):
    def __init__(self, text="", text_size=30, h=150, w=250, offset=20, color="#3cc21b", parent=None, style=None):
        super(PlayButton, self).__init__(text, text_size, h, w, offset, color, style, parent)
        self.pressed.connect(self._play_pause)

    def _play_pause(self):
        print("Play/Pause")
        # Call parent


class CloseButton(FrameButton):
    def __init__(self, text="", text_size=30, h=150, w=250, offset=20, color="#c21b1b", parent=None, style=None):
        super(CloseButton, self).__init__(text, text_size, h, w, offset, color, style, parent)
        self.pressed.connect(self._close)
    def _close(self):
        print("Close")
        sys.exit(app.exec_())


class ListVideoPlayer(QWidget):
    def __init__(self, graphic_item=False, parent=None, margin=0.8):
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

        self.play_button = PlayButton(text="PAUSAR")
        self.close_button = CloseButton(text="CERRAR")
        self._button_layout.addWidget(self.play_button)
        self._button_layout.addWidget(self.close_button)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.setAlignment(self.play_button, Qt.AlignCenter)
        self._main_layout.setContentsMargins(4, 4, 4, 8)
        self._frame_layout.setContentsMargins(0, 0, 0, 4)

        self._frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setLayout(self._main_layout)

        desktop_widget = QApplication.desktop().screenGeometry(0)
        self.setFixedSize(desktop_widget.width() * margin, desktop_widget.height() * margin)
        self.setMaximumSize(desktop_widget.width() * margin, desktop_widget.height() * margin)
        self.move(desktop_widget.width() * (1 - margin) / 2, desktop_widget.height() * (1 - margin) / 2)
        print(desktop_widget.center())
        print(self.sizeHint())
        print(self._frame.sizeHint())
        # self._played_videos = 0
        # # self.audio.setVolume(50)
        self._media_player.stateChanged.connect(self.handle_state_changed)
        # self._reproduce_multiple = False

    # def handleButton(self):
    #     if self._media_player.state() == QMediaPlayer.PlayingState:
    #         self._media_player.stop()
    #     else:
    #         path = QtGui.QFileDialog.getOpenFileName(self, self.button.text())
    #         if path:
    #             self._media_player.setCurrentSource(QMediaPlayer.MediaSource(path))
    #             self._media_player.play()
    #
    def handle_state_changed(self, newstate):
        print(newstate)

    #
    def set_video_list(self, video_list_path):
        for path in video_list_path:
            self.add_path_to_video_list(path)

    #
    def add_path_to_video_list(self, video_path):
        if os.path.exists(video_path):
            self._full_media_list.append(video_path)
            return len(self._full_media_list) - 1
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), video_path)
            return -1

    #
    #
    def play_indexes_list(self, video_indexes):
        self._current_play_list.clear()
        for index in video_indexes:
            if index in range(len(self._full_media_list)):
                path = self._full_media_list[index]
                self._current_play_list.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self._media_player.play()

    #
    def reproduce_all(self):
        self._current_play_list.addMedia(self._full_media_list)

    def clear(self):
        self._current_play_list.clear()

    #
    # def check_and_play(self, video_index):
    #     if video_index in range(len(self._video_list)):
    #         next_path = self._video_list[video_index]
    #         self._media_player.setCurrentSource(Phonon.MediaSource(next_path))
    #         self._media_player.play()
    #     else:
    #         print("Video index out of video list (%d of %d)"%(len(video_index, len(self._video_list))))


class ActionsVideoPlayer(ListVideoPlayer):
    def __init__(self, parent=None):
        super(ActionsVideoPlayer, self).__init__(parent)
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []
        # TODO: Only needed becuase the problem with QVideoWidget and QGraphicScene
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

    def add_action(self, action_key, clip_path, action_index=-1):
        if action_index < 0:
            next_index = len(self._actions_list)
        else:
            if action_index not in self._index_to_key.keys():
                next_index = action_index
            else:
                raise IndexError("Trying to use already existing index %d for action '%s'" % (action_index, action_key))

        self._actions_list[action_key] = {"index": next_index, "clip_path": clip_path}
        # save the action name by index
        self._index_to_key[next_index] = action_key
        # save the index in the playlist
        self._index_to_playlist[action_key] = self.add_path_to_video_list(clip_path)

    def play_one_action(self, action_key):
        play_list_index = self._index_to_playlist[action_key]
        if [play_list_index] != self._currently_playing or self._media_player.state() != QMediaPlayer.PlayingState:
            print("To play")
            self.play_indexes_list([play_list_index])
            self._currently_playing = [play_list_index]

    def stop(self):
        print("To stop")
        self._media_player.stop()
        self._current_play_list.clear()

    def clear(self):
        print("To clear")
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []
        super(ActionsVideoPlayer, self).clear()

    def __contains__(self, key):
        return key in self._actions_list.keys()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ActionsVideoPlayer()

    window.add_action("action_1",
                      "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/final_game1/videos/action_1.MP4",
                      1)
    window.add_action("action_2",
                      "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/final_game1/videos/action_2.MP4",
                      2)
    window.play_one_action("action_1")
    # window.setFixedSize(200,240)

    # mypath = "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/clothclean/LEJOS"
    # onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".mp4")]
    # window.set_video_list(onlyfiles)
    window.show()
    # window.play_indexes_list([0,1,4])
    sys.exit(app.exec_())
