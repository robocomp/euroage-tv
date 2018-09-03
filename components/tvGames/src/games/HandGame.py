import cv2
import sys

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget
from libs.Hand_Detection.HandDetection import HandDetector
from libs.QImageWidget import QImageWidget


class HandGame(QMainWindow):
    def __init__(self, parent=None):
        super(HandGame, self).__init__(parent)
        self.detector = HandDetector(source=-1)
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.add_player_button = QPushButton("Add new player")
        self.add_player_button.clicked.connect(self.add_new_player_clicked)
        self.main_layout.addWidget(self.add_player_button)

        self.reset_background_button = QPushButton("Reset background")
        self.reset_background_button.clicked.connect(self.reset_background_clicked)
        self.main_layout.addWidget(self.reset_background_button)

        self.main_layout.addWidget(self.add_player_button)
        self.image_widget = QImageWidget()
        self.image_widget.show()
        # self.capture = cv2.VideoCapture('/home/robolab/PycharmProjects/TVGames/libs/Hand_Detection/resources/testing_hand_video.mp4')
        self.capture = cv2.VideoCapture(0)
        self.last_frame = None
        self.current_state = "main"
        self.players = 0
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.main_loop)
        self.game_timer.start(1000 / 24)
        self.tv_widget = QImageWidget()
        # self.tv_widget.show_on_second_screen()
        self.tv_widget.show()



    def add_new_player_clicked(self):
        if self.current_state == "main":
            self.current_state = "adding_player"
            self.players += 1

    def reset_background_clicked(self):
        self.detector.reset_background()


    def main_loop(self):
        if self.capture.isOpened():

            # Measure execution time
            # start_time = time.time()

            # Capture frames from the camera
            ret, frame = self.capture.read()
            if ret:
                self.last_frame = frame
                if self.current_state == "main":
                    self.detector.update_detection_and_tracking(frame)
                    overlayed_frame = self.detector.compute_overlayed_frame(frame)
                    self.image_widget.set_opencv_image(overlayed_frame, BGR=False)
                    if self.players > len(self.detector.hands):
                        self.current_state = "adding_player"
                elif self.current_state == "adding_player":
                    if self.players > len(self.detector.hands):
                        print "Waiting for new hand"
                        new_hand_frame = self.detector.add_hand2(frame)
                        self.image_widget.set_opencv_image(frame)
                        self.tv_widget.set_opencv_image(new_hand_frame)
                    else:
                        print "New player added"
                        self.current_state = "main"
                        self.image_widget.set_opencv_image(frame)
                else:
                    self.image_widget.set_opencv_image(frame)




def main():
    app = QApplication([])

    hand_game = HandGame()
    hand_game.show()
    hand_game.main_loop()
    sys.exit(app.exec_())

    # game = ImageGame()
    # game.game_loop()


if __name__ == '__main__':
    main()