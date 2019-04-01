import signal
import sys

from PySide2.QtCore import QObject, Signal, QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QLabel, QGroupBox, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication,QStackedWidget


class LoginWindow(QWidget): # crea widget vacio
    def __init__(self,parent = None):

        super(LoginWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(LoginWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/login.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()



class RegisterWindow(QWidget): # crea widget vacio
    def __init__(self,parent = None):
        super(RegisterWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(RegisterWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/register.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()

class UsersWindow(QWidget): # crea widget vacio
    def __init__(self,parent = None):
        super(UsersWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(UsersWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/usersv2.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()

class PlayersWindow(QWidget): # crea widget vacio
    def __init__(self,parent = None):
        super(PlayersWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(PlayersWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/player.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()

class GameWindow(QWidget): # crea widget vacio
    def __init__(self,parent = None):
        super(GameWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(GameWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/adminGame/src/AdminInterface.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0,0,0,0)
        file.close()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # login = LoginWindow()
    # login.show()
    #
    # register = RegisterWindow()
    # register.show()
    #
    # users = UsersWindow()
    # users.show()

    player = PlayersWindow()
    player.show()
    #
    # game = GameWindow()
    # game.show()

    app.exec_()