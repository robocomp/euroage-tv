import os
import signal
import sys
from collections import OrderedDict
from PySide2.QtCore import QFile, QEvent, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox, QFileDialog, QDialog
import json

try:
    from games.draganddropgame.draganddropgame import GameScreen
except:
    print("Added src to python path")
    sys.path.append('../src/')
    from games.draganddropgame.draganddropgame import GameScreen


class PieceWindow(QDialog):
    def __init__(self, parent=None):
        super(PieceWindow, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        loader = QUiLoader()
        loader.registerCustomWidget(PieceWindow)
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/tools/piece.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        # self.mylayout.setContentsMargins(0, 0, 0, 0)
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
        file = QFile("/home/robocomp/robocomp/components/euroage-tv/components/tvGames/tools/game_editor_test.ui")
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
        self.current_piece = PieceWindow(self)
        self.current_piece.ui.save_button.clicked.connect(self.save_piece)
        self.current_piece.ui.name_lineEdit.clear()
        self.current_piece.ui.index_sb.setValue(len(self.pieces)+1)

        self.current_piece.ui.image_path_lineEdit.clear()
        self.current_piece.ui.video_path_lineEdit.clear()
        self.current_piece.ui.piece_pos_x_sb.setValue(5+int(len(self.pieces)*self.ui.piece_width_sb.value() + 5*len(self.pieces)))

        # self.current_piece.ui.piece_pos_x_sb.setValue(10)
        self.current_piece.ui.piece_pos_y_sb.setValue(20)
        # self.current_piece.ui.piece_pos_y_sb.setValue(10)
        # ############### TESTING #########3
        key = "una bonita pieza"
        self.current_piece.ui.name_lineEdit.setText(key)
        self.current_piece.ui.image_path_lineEdit.setText(
            "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/resources/HACER TORTILLA/photos/action_1.jpg")
        self.current_piece.ui.video_path_lineEdit.setText(
            "/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/resources/HACER TORTILLA/videos/action_1.MP4")
        # ############### TESTING #########3
        self.current_piece.show()

    def show_piece(self, item):
        item_name = item.text()
        self.modifying_key = item_name
        self.current_piece = self.pieces[item_name]
        self.current_piece.ui.save_button.clicked.disconnect()
        self.current_piece.ui.save_button.clicked.connect(self.modify_piece)
        self.current_piece.show()


    def save_piece(self):
        key = self.current_piece.ui.name_lineEdit.text()
        if key != "":
            if key not in self.pieces:
                print ("Saving piece...")
                print ("Name", key)
                print ("Position", self.current_piece.ui.index_sb.value())
                print ("Image Path", self.current_piece.ui.image_path_lineEdit.text())
                print ("Video Path", self.current_piece.ui.video_path_lineEdit.text())

                self.pieces[key] = self.current_piece
                self.ui.pieces_listWidget.addItem(key)

            else:
                QMessageBox().information(self.focusWidget(), 'Error',
                                          'El nombre de la pieza ya existe',
                                          QMessageBox.Ok)
        self.current_piece.hide()

    def modify_piece(self):
        original_key = self.modifying_key
        current_key = self.current_piece.ui.name_lineEdit.text()
        self.pieces[current_key]=self.pieces.pop(original_key)
        listwidget_item = self.ui.pieces_listWidget.findItems(original_key,Qt.MatchExactly)[0]
        listwidget_item.setText(current_key)
        self.current_piece.hide()

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

        open_hand_icon = OrderedDict()
        open_hand_icon["size"] = [100, 100]
        open_hand_icon["initial_pose"] = [400, 300]
        open_hand_icon["image_path"] = "../../resources/common/icons/00-Pointer-Hand-icon_2.png"
        open_hand_icon["name"] = "handOpen"
        open_hand_icon["category"] = "mouse"
        pieces_dict["handOpen"] = open_hand_icon
        close__hand_icon = OrderedDict()
        close__hand_icon["size"] = [100, 100]
        close__hand_icon["initial_pose"] = [400, 300]
        close__hand_icon["image_path"] = "../../resources/common/icons/01-Pointer-Hand-icon_2.png"
        close__hand_icon["name"] = "handClose"
        close__hand_icon["category"] = "mouse"
        pieces_dict["handClose"] = open_hand_icon
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
