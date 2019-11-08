import os
import signal
import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QPushButton, QLabel, QSizePolicy

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
UIS_FOLDER = os.path.join(CURRENT_FILE_PATH, "uis" )


class MyQMessageBox(QMessageBox):
    def __init__(self, *args):
        super(MyQMessageBox, self).__init__(*args)

    @staticmethod
    def show_information(parent, title, message, button_text="Vale", button_role=QMessageBox.YesRole):
        message_box = QMessageBox(parent)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        message_box.setSizeGripEnabled(True)
        message_box.setStyleSheet(
            "QPushButton {"
            " font: 30px;"
            " min-height: 50px;"
            " min-width: 100px;"
            "}"
            "QLabel {"
            "font: 30px;"
            "}"
        )
        message_box.addButton(button_text, button_role)
        return message_box.exec_()

    @staticmethod
    def show_question(parent, title, message, button_text="Vale", button_role=QMessageBox.YesRole):
        message_box = QMessageBox(parent)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        message_box.setSizeGripEnabled(True)
        message_box.setStyleSheet(
            "QPushButton {"
            " font: 30px;"
            " min-height: 50px;"
            " min-width: 100px;"
            "}"
            "QLabel {"
            "font: 30px;"
            "}"
        )
        message_box.addButton("Si", QMessageBox.YesRole)
        message_box.addButton("No", QMessageBox.NoRole)
        return message_box.exec_()

    @staticmethod
    def information(parent, title, text, button0=None, button1=None):
        return MyQMessageBox.show_information(parent=parent, title=title, message=text)

    @staticmethod
    def question(parent, title, text, button0=None, button1=None):
        return MyQMessageBox.show_question(parent=parent, title=title, message=text)


# TODO:  try to unifiy the repeated code.
class LoginWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(LoginWindow)
        file = QFile(os.path.join(UIS_FOLDER, "big", "login.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


class RegisterWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(RegisterWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(RegisterWindow)
        file = QFile(os.path.join(UIS_FOLDER,"big", "register.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


class UsersWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(UsersWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(UsersWindow)
        file = QFile(os.path.join(UIS_FOLDER,"big", "usersv2.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


class PlayersWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(PlayersWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(PlayersWindow)
        file = QFile(os.path.join(UIS_FOLDER,"big", "player.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


class GameWindow(QWidget):
    """
    This is the widget for the GameWindow.
    """
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(GameWindow)
        file = QFile(os.path.join(UIS_FOLDER,"big", "AdminInterface.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    login = LoginWindow()
    login.show()

    register = RegisterWindow()
    register.show()

    users = UsersWindow()
    users.show()

    player = PlayersWindow()
    player.show()

    game = GameWindow()
    game.show()

    app.exec_()
