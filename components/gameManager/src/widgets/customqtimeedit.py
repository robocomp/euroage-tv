from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStyle, QDialog, QDialogButtonBox


class CustomTimeEditDialog(QDialog):
    def __init__(self, parent=None, default_seconds=120):
        super(CustomTimeEditDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setObjectName("CustomTimeEditDialog")
        self.setWindowTitle("")
        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)
        self.__label = QLabel(self.tr("Seleccione el tiempo\npara este juego"))
        self.__label.setAlignment(Qt.AlignCenter)
        f = QFont("Arial", 14, QFont.Bold)
        self.__label.setFont(f)
        self.__main_layout.addWidget(self.__label)
        self.__time_edit = CustomQTimeEdit(default_seconds)
        self.__main_layout.addWidget(self.__time_edit)
        self.__buttons_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__main_layout.addWidget(self.__buttons_box)
        self.__buttons_box.rejected.connect(self.close)
        self.__buttons_box.accepted.connect(self.accept)
        self.setWindowModality(Qt.WindowModal)

    @property
    def seconds(self):
        return self.__time_edit.seconds


class CustomQTimeEdit(QWidget):
    def __init__(self, default_seconds=60, parent=None):
        super(CustomQTimeEdit, self).__init__(parent)

        self.__seconds = default_seconds

        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

        self.__down_arrows_layout = QHBoxLayout()
        self.__up_arrows_layout = QHBoxLayout()

        f = QFont("Arial", 50, QFont.Bold)
        self.__time_label = QLabel("00:00", self)
        self.__time_label.setFont(f)
        self.__time_label.setAlignment(Qt.AlignCenter)

        self.__minutes_up_button = QPushButton()
        self.__minutes_up_button.setAutoRepeat(True)
        self.__minutes_up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.__seconds_up_button = QPushButton()
        self.__seconds_up_button.setAutoRepeat(True)
        self.__seconds_up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.__up_arrows_layout.addWidget(self.__minutes_up_button)
        self.__up_arrows_layout.addWidget(self.__seconds_up_button)

        self.__minutes_down_button = QPushButton()
        self.__minutes_down_button.setAutoRepeat(True)
        self.__minutes_down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.__seconds_down_button = QPushButton()
        self.__seconds_down_button.setAutoRepeat(True)
        self.__seconds_down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.__down_arrows_layout.addWidget(self.__minutes_down_button)
        self.__down_arrows_layout.addWidget(self.__seconds_down_button)

        self.__main_layout.addLayout(self.__up_arrows_layout)
        self.__main_layout.addWidget(self.__time_label)
        self.__main_layout.addLayout(self.__down_arrows_layout)

        self.__minutes_up_button.pressed.connect(self.up_minutes)
        self.__minutes_down_button.pressed.connect(self.down_minutes)
        self.__seconds_up_button.pressed.connect(self.up_seconds)
        self.__seconds_down_button.pressed.connect(self.down_seconds)
        self.update_label()

    def up_minutes(self):
        self.__seconds += 60
        self.update_label()

    def down_minutes(self):
        self.__seconds -= 60
        self.update_label()

    def up_seconds(self):
        self.__seconds += 1
        self.update_label()

    def down_seconds(self):
        self.__seconds -= 1
        self.update_label()

    def update_label(self):
        if self.__seconds < 0:
            self.__seconds = 0
        minutes = int(self.__seconds / 60)
        seconds = int(self.__seconds % 60)
        self.__time_label.setText("%02d:%02d" % (minutes, seconds))

    @property
    def seconds(self):
        return self.__seconds
