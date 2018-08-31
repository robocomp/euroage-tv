import sys

from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QApplication


class QTestingWidget(QWidget):
    def __init__(self, parent=None):
        super(QTestingWidget, self).__init__(parent)


        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.add_player_button = QPushButton("Add new player")
        self.main_layout.addWidget(self.add_player_button)
        self.setWindowTitle("Testing widget")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = QTestingWidget()
    test.show()
    app.exec_()
