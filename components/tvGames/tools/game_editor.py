import signal
import sys

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication


class PieceWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(PieceWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(PieceWindow)
        file = QFile("/home/robolab/game_editor/piece.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()


class EditorWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(EditorWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(EditorWindow)
        file = QFile("/home/robolab/game_editor/game_editor_test.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()

        self.pieces = {}
        self.current_piece = None

        self.ui.add_piece_button.clicked.connect(self.open_piece_window)
        self.ui.delete_piece_button.clicked.connect(self.delete_piece)
        self.ui.pieces_listWidget.itemDoubleClicked.connect(self.show_piece)


    def open_piece_window(self):
        print("Creating piece")
        self.current_piece = PieceWindow()
        self.current_piece.ui.save_button.clicked.connect(self.save_piece)
        self.current_piece.ui.name_lineEdit.clear()
        self.current_piece.ui.index_sb.setValue(0)

        self.current_piece.ui.image_path_lineEdit.clear()
        self.current_piece.ui.video_path_lineEdit.clear()
        self.current_piece.show()

    def show_piece(self,item):
        item_name = item.text()
        self.pieces[item_name].show()

    def save_piece(self):
        key = self.current_piece.ui.name_lineEdit.text()
        if key != "":
            print ("Saving piece...")
            print ("Name", key)
            print ("Position", self.current_piece.ui.index_sb.value())
            print ("Image Path", self.current_piece.ui.image_path_lineEdit.text())
            print ("Video Path", self.current_piece.ui.video_path_lineEdit.text())

            self.pieces[key] = self.current_piece
            self.ui.pieces_listWidget.addItem(key)
            self.current_piece.hide()

    def delete_piece(self):
        key = self.ui.pieces_listWidget.currentItem().text()
        self.pieces.pop(key)
        item_to_delete = self.ui.pieces_listWidget.currentRow()
        self.ui.pieces_listWidget.takeItem(item_to_delete)
        print(len(self.pieces))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    editor = EditorWindow()
    editor.show()

    print(editor.ui.title_lineEdit.text())

    app.exec_()
