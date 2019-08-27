import os
import signal
import sys
from collections import OrderedDict
from PySide2.QtCore import QFile, QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QFileDialog, QDialog
import json

from games.draganddropgame.draganddropgame import GameScreen

class PieceWindow(QWidget):
class PieceWindow(QDialog):
    def __init__(self, parent=None):
        super(PieceWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(PieceWindow)
        file = QFile("/home/robolab/robocomp/components/euroage-tv/components/tvGames/tools/piece.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()
        self.ui.image_path_lineEdit.installEventFilter(self)
        self.ui.video_path_lineEdit.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonDblClick:
            filePath =  None
            accepted = False
            if watched == self.ui.image_path_lineEdit:
                filePath, accepted = QFileDialog.getOpenFileName(self, "Open File",
                                                          '' , "IMAGE files (*.jpeg *.jpg *.png)")
            if watched == self.ui.video_path_lineEdit:
                filePath, accepted = QFileDialog.getOpenFileName(self, "Open File",
                                                                 '', "MP4 files (*.mp4 *.MP4)")
            if filePath is not None and accepted:
                watched.setText(filePath)
        return QWidget.eventFilter(self, watched, event)


class EditorWindow(QWidget):  # crea widget vacio
    def __init__(self, parent=None):
        super(EditorWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(EditorWindow)
        file = QFile("/home/robolab/robocomp/components/euroage-tv/components/tvGames/tools/game_editor_test.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()
        self._view = GameScreen()
        # self.ui.pieces_hl.addWidget(self._view)
        self.pieces = {}
        self.current_piece = None

        self.ui.add_piece_button.clicked.connect(self.open_piece_window)
        self.ui.delete_piece_button.clicked.connect(self.delete_piece)
        self.ui.pieces_listWidget.itemDoubleClicked.connect(self.show_piece)
        self.ui.generate_button.clicked.connect(self.generate_dict)

    def open_piece_window(self):
        print("Creating piece")
        self.current_piece = PieceWindow()
        self.current_piece.ui.save_button.clicked.connect(self.save_piece)
        self.current_piece.ui.name_lineEdit.clear()
        self.current_piece.ui.index_sb.setValue(0)

        self.current_piece.ui.image_path_lineEdit.clear()
        self.current_piece.ui.video_path_lineEdit.clear()
        self.current_piece.show()

    def show_piece(self, item):
        item_name = item.text()
        self.pieces[item_name].show()

    def save_piece(self):
        key = self.current_piece.ui.name_lineEdit.text()
        if key != "":
            if key not in self.pieces.keys():
                print ("Saving piece...")
                print ("Name", key)
                print ("Position", self.current_piece.ui.index_sb.value())
                print ("Image Path", self.current_piece.ui.image_path_lineEdit.text())
                print ("Video Path", self.current_piece.ui.video_path_lineEdit.text())

                self.pieces[key] = self.current_piece
                self.ui.pieces_listWidget.addItem(key)
                self.current_piece.hide()

            else:
                QMessageBox().information(self.focusWidget(), 'Error',
                                          'El nombre de la pieza ya existe',
                                          QMessageBox.Ok)

    def delete_piece(self):
        key = self.ui.pieces_listWidget.currentItem().text()
        self.pieces.pop(key)
        item_to_delete = self.ui.pieces_listWidget.currentRow()
        self.ui.pieces_listWidget.takeItem(item_to_delete)
        print(len(self.pieces))

    def generate_dict(self):
        game_dict = OrderedDict()

        game_dict["title"] = self.ui.title_lineEdit.text()
        game_dict["size"] = [self.ui.game_width_sb.value(), self.ui.game_height_sb.value()]
        game_dict["difficult"] = self.ui.difficulty_sb.value()
        game_dict["time"] = self.ui.time_sb.value()
        game_dict["depth"] = {"destination": "0", "piece": "10", "mouse": "50"}

        piece_size = [self.ui.piece_width_sb.value(), self.ui.piece_height_sb.value()]
        pieces_dict = {}

        for name, piece in self.pieces.items():
            index = piece.ui.index_sb.value()
            action_name = "action_" + str(index)

            attributes_dict = OrderedDict()
            attributes_dict["index"] = index
            attributes_dict["title"] = name
            attributes_dict["size"] = piece_size

            attributes_dict["initial_pose"] = [piece.ui.piece_pos_x_sb.value(), piece.ui.piece_pos_y_sb.value()]
            attributes_dict["final_pose"] = [piece.ui.piece_pos_x_sb.value(), piece.ui.piece_pos_y_sb.value() + self.ui.piece_height_sb.value()*2+10]

            attributes_dict["image_path"] = piece.ui.image_path_lineEdit.text()
            attributes_dict["video_path"] = piece.ui.video_path_lineEdit.text()
            attributes_dict["name"] = action_name
            attributes_dict["category"] = "piece"

            pieces_dict[action_name] = attributes_dict

        game_dict["images"] = pieces_dict

        with open('./game.json', 'w') as file:
            json.dump(game_dict, file, indent=4)
            print("Saved json file")
        self._view.init_game(os.path.abspath("./game.json"))
        self._view.show_on_second_screen()
        self._view._game_frame.adjust_view()
        print(self._view._game_frame._scene.sceneRect())
        print(self._view._game_frame._view.sceneRect())
        for piece in self._view._game_frame._pieces:
            print("piece size: ", piece.width, piece.height)






if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    editor = EditorWindow()
    editor.showMaximized()

    app.exec_()
