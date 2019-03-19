import errno
import os
from time import sleep
from collections import OrderedDict
from ptyprocess.ptyprocess import FileNotFoundError

from PySide2.QtCore import QUrl, Qt
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import QVBoxLayout, QFrame, QWidget, QApplication, QLabel


class ListVideoPlayer(QWidget):
    def __init__(self, graphic_item = False, parent=None):
        super(ListVideoPlayer, self).__init__(parent=parent)
        self._frame = QFrame()

        self._media_player = QMediaPlayer(self)
        self._video_widget = QVideoWidget(self._frame)
        self._current_play_list = QMediaPlaylist()
        self._media_player.setVideoOutput(self._video_widget)
        self._media_player.setPlaylist(self._current_play_list)
        self._frame_layout = QVBoxLayout()

        self._frame.setLayout(self._frame_layout)
        self._frame_layout.addWidget(self._video_widget)
        self._full_media_list = []
        # self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
        # Phonon.createPath(self.media, self.audio)
        # Phonon.createPath(self.media, self.video)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._frame, 1)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._frame_layout.setContentsMargins(4,4,4,4)
        self._frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setLayout(self._main_layout)
        self.setMaximumSize(640,480)
        print  self.sizeHint()
        print  self._frame.sizeHint()
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
    def add_path_to_video_list(self,video_path):
        if os.path.exists(video_path):
            self._full_media_list.append(video_path)
            return len(self._full_media_list)-1
        else:
            raise FileNotFoundError( errno.ENOENT, os.strerror(errno.ENOENT), video_path)
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
    def __init__(self, parent = None):
        super(ActionsVideoPlayer, self).__init__(parent)
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []
        # TODO: Only needed becuase the problem with QVideoWidget and QGraphicScene
        self.setWindowFlags(Qt.WindowStaysOnTopHint| Qt.FramelessWindowHint)


    def add_action(self, action_key, clip_path, action_index=-1):
        if action_index <0:
            next_index = len(self._actions_list)
        else:
            if action_index not in self._index_to_key.keys():
                next_index = action_index
            else:
                raise IndexError("Trying to use already existing index %d for action '%s'" % (action_index, action_key))

        self._actions_list[action_key] = {"index": next_index, "clip_path":clip_path}
        # save the action name by index
        self._index_to_key[next_index] = action_key
        # save the index in the playlist
        self._index_to_playlist[action_key] = self.add_path_to_video_list(clip_path)

    def play_one_action(self, action_key):
        play_list_index = self._index_to_playlist[action_key]
        if [play_list_index] != self._currently_playing or self._media_player.state() != QMediaPlayer.PlayingState:
            print "To play"
            self.play_indexes_list([play_list_index])
            self._currently_playing = [play_list_index]

    def stop(self):
        print "To stop"
        self._media_player.stop()
        self._current_play_list.clear()

    def clear(self):
        print "To clear"
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []
        super(ActionsVideoPlayer, self).clear()

    def __contains__(self, key):
        return key in self._actions_list.keys()



if __name__ == '__main__':
    import sys


    app = QApplication(sys.argv)
    window = ActionsVideoPlayer()
    from os import listdir
    from os.path import isfile, join


    window.add_action("action_1", "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/final_game1/videos/action_1.MP4", 1)
    window.add_action("action_2", "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/final_game1/videos/action_2.MP4", 2)
    window.play_one_action("action_1")
    # window.setFixedSize(200,240)


    # mypath = "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/genericDragGame/resources/clothclean/LEJOS"
    # onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".mp4")]
    # window.set_video_list(onlyfiles)
    window.show()
    # window.play_indexes_list([0,1,4])
    sys.exit(app.exec_())
