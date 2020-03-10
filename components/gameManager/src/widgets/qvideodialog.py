


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The initial video screen
import signal
import sys

from PySide2.QtCore import QUrl, Signal
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import QApplication, QDialog, QVBoxLayout

import os
dirname = os.path.dirname(__file__)

class QVideoDialog(QDialog):
    video_stopped = Signal()
    def __init__(self, parent=None):
        super(QVideoDialog, self).__init__(parent)
        self.__video_widget = QVideoWidget()
        self.__video_player = QMediaPlayer()
        self.__video_player.mediaStatusChanged.connect(self.video_available_changed)
        self.__video_player.stateChanged.connect(self.player_status_changed)
        self.__video_player.setVideoOutput(self.__video_widget)
        self.__video_player.setMedia(QUrl.fromLocalFile(os.path.join(dirname, "..","resources","Intro.mp4")))
        self.__main_layout = QVBoxLayout()
        self.__main_layout.setSpacing(0)
        self.__main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.__main_layout)
        self.__main_layout.addWidget(self.__video_widget)


    def video_available_changed(self, available):
        if available:
            self.__video_widget.updateGeometry()
            self.__video_widget.adjustSize()
            self.adjustSize()

    def play(self):
        self.__video_player.play()

    def player_status_changed(self, status):
        if status == QMediaPlayer.StoppedState:
            self.video_stopped.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QVideoDialog()
    a.showFullScreen()
    a.play()
    app.exec_()
