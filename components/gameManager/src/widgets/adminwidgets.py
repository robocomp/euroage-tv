import os
import signal
import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QPushButton, QLabel, QSizePolicy

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
UIS_FOLDER = os.path.join(CURRENT_FILE_PATH, "../uis")


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
        message_box.setStandardButtons(QMessageBox.Ok)
        button_accept = message_box.button(QMessageBox.Ok)
        button_accept.setText(message_box.tr('Vale'))
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
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = message_box.button(QMessageBox.Yes)
        buttonY.setText(message_box.tr('Si'))
        buttonN = message_box.button(QMessageBox.No)
        buttonN.setText(message_box.tr('No'))
        message_box.setDefaultButton(QMessageBox.Yes)
        return message_box.exec_()

    @staticmethod
    def information(parent, title, text, button0=None, button1=None):
        return MyQMessageBox.show_information(parent=parent, title=title, message=text)

    @staticmethod
    def question(parent, title, text, button0=None, button1=None):
        return MyQMessageBox.show_question(parent=parent, title=title, message=text)


class FileWidgetLoader(QWidget):
    def __init__(self, filename, type="big", parent=None):
        super(FileWidgetLoader, self).__init__(parent)
        self.__mylayout = QVBoxLayout()
        self.setLayout(self.__mylayout)
        loader = QUiLoader()
        loader.setLanguageChangeEnabled(True)
        # loader.registerCustomWidget(FileWidgetLoader)
        file = QFile(os.path.join(UIS_FOLDER, type, filename))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.__mylayout.addWidget(self.ui)
        self.__mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


# TODO:  try to unifiy the repeated code.
class LoginWindow(FileWidgetLoader):  # crea widget vacio
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__("login.ui", "big", parent)


class RegisterWindow(FileWidgetLoader):  # crea widget vacio
    def __init__(self, parent=None):
        super(RegisterWindow, self).__init__("register.ui", "big", parent)


class UsersWindow(FileWidgetLoader):  # crea widget vacio
    def __init__(self, parent=None):
        super(UsersWindow, self).__init__("usersv2.ui", "big", parent)


class PlayersWindow(FileWidgetLoader):  # crea widget vacio
    def __init__(self, parent=None):
        super(PlayersWindow, self).__init__("player.ui", "big", parent)


class GameWindow(FileWidgetLoader):
    """
    This is the widget for the GameWindow.
    """

    def __init__(self, parent=None):
        super(GameWindow, self).__init__("AdminInterface.ui", "big", parent)


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
