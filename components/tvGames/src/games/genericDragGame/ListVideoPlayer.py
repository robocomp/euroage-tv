import errno
import os
from PyQt4 import QtGui
from collections import OrderedDict
from ptyprocess.ptyprocess import FileNotFoundError

from PyQt4.QtGui import QFrame, QVBoxLayout
from PyQt4.phonon import Phonon



class ListVideoPlayer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ListVideoPlayer, self).__init__(parent=parent)
        self._frame = QFrame()

        self.media = Phonon.MediaObject(self)
        self.video = Phonon.VideoWidget(self._frame)
        self._frame_layout = QVBoxLayout()

        self._frame.setLayout(self._frame_layout)
        self._frame_layout.addWidget(self.video)
        # self.video.setMinimumSize(400, 400)
        self.audio = Phonon.AudioOutput(Phonon.VideoCategory, self)
        Phonon.createPath(self.media, self.audio)
        Phonon.createPath(self.media, self.video)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._frame, 1)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._frame_layout.setContentsMargins(4,4,4,4)
        self._frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self._video_list = []
        self._played_videos = 0
        self.audio.setVolume(50)
        self.media.stateChanged.connect(self.handle_state_changed)
        self._reproduce_multiple = False

    def handleButton(self):
        if self.media.state() == Phonon.PlayingState:
            self.media.stop()
        else:
            path = QtGui.QFileDialog.getOpenFileName(self, self.button.text())
            if path:
                self.media.setCurrentSource(Phonon.MediaSource(path))
                self.media.play()

    def handle_state_changed(self, newstate, oldstate):
        if newstate != Phonon.LoadingState and newstate != Phonon.BufferingState:
            if newstate == Phonon.ErrorState:
                source = self.media.currentSource().fileName()
                print('ERROR: could not play:', source.toLocal8Bit().data())
                print('  %s' % self.media.errorString().toLocal8Bit().data())
        if oldstate == Phonon.PlayingState and self._reproduce_multiple:
            self._played_videos += 1
            if self._played_videos < len(self._playing_indexes):
                if self._playing_indexes[self._played_videos] in  range(len(self._video_list)):
                    self.check_and_play(self._playing_indexes[self._played_videos])
            else:
                print("Reproduction ended")

    def set_video_list(self, video_list_path):
        for path in video_list_path:
            self.add_path_to_video_list(path)

    def add_path_to_video_list(self,video_path):
        if os.path.exists(video_path):
            self._video_list.append(video_path)
            return len(self._video_list)-1
        else:
            raise FileNotFoundError( errno.ENOENT, os.strerror(errno.ENOENT), video_path)
            return -1


    def play_indexes_list(self, video_indexes):
        self._reproduce_multiple = True
        self._playing_indexes = video_indexes
        self.check_and_play(self._playing_indexes[0])

    def reproduce_all(self):
        self.play_indexes_list(range(len(self._video_list)))

    def check_and_play(self, video_index):
        if video_index in range(len(self._video_list)):
            next_path = self._video_list[video_index]
            self.media.setCurrentSource(Phonon.MediaSource(next_path))
            self.media.play()
        else:
            print("Video index out of video list (%d of %d)"%(len(video_index, len(self._video_list))))

class ActionsVideoPlayer(ListVideoPlayer):
    def __init__(self, parent = None):
        super(ActionsVideoPlayer, self).__init__(parent)
        self._actions_list = OrderedDict()
        # index from index number of actions to action keys (names)
        self._index_to_key = {}
        self._index_to_playlist = {}
        self._currently_playing = []

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
        self.video.show()
        play_list_index = self._index_to_playlist[action_key]
        if [play_list_index] != self._currently_playing or self.media.state() != Phonon.PlayingState:
            self.play_indexes_list([play_list_index])
            self._currently_playing = [play_list_index]

    def stop(self):
        self.media.stop()
        self.media.clear()

    def __contains__(self, key):
        return key in self._actions_list.keys()



if __name__ == '__main__':
    import sys


    app = QtGui.QApplication(sys.argv)
    window = ListVideoPlayer()
    from os import listdir
    from os.path import isfile, join
    mypath = "//home//robolab//robocomp//components//euroage-tv//components//tvGames//src//games//genericDragGame//resources//videos"
    onlyfiles = [os.path.join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
    window.set_video_list(onlyfiles)
    window.show()
    window.play_indexes_list([0,3,4])
    sys.exit(app.exec_())
