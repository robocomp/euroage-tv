#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys
from pprint import pprint

from PyQt4.QtCore import QAbstractTableModel, QString, Qt, QVariant, QStringList
from PyQt4.QtGui import QApplication, QTableView, QWidget, QVBoxLayout, QComboBox, QHBoxLayout

"""
{
  "Esteban":
  {
    "Nick": "orensbruli",
    "Games":
    {
      "Selecciona la imagen":
      {
        "Times": 13,
        "Seconds played": 1890,
        "Last time": 123213213123,
        "Best Score": 5731,
        "Last Scores": [2300, 1000, 5000, 127, 48]

      }
    }
  },
  "Ramon":
  {
    "Nick": "raimon",
    "Games":
    {
      "Selecciona la imagen":
      {
        "Times": 13,
        "Seconds played": 1890,
        "Last time": 123213213123,
        "Best Score": 5731,
        "Last Scores": [2300, 1000, 5000, 127, 48]

      },
      "Escoge tu ropa":
      {
        "Times": 2,
        "Seconds played": 30,
        "Last time": 121313213123,
        "Best Score": 299,
        "Last Scores": [2300, 1000, 5000, 127, 48]
      }
    }
  }
}
"""


class QScoreBoardTableModel(QAbstractTableModel):
	def __init__(self, parent=None):
		super(QScoreBoardTableModel, self).__init__(parent)
		self.scores = {}
		self.players_index = []
		self.header = ["Name", "Best Score", "Times played", "Total time played"]
		# TODO: set to None
		self.current_game = "Escoge tu ropa"

	def rowCount(self, index=None):
		return len(self.scores)

	def columnCount(self, index=None):
		return 2

	def data(self, index, role=None):
		if not index.isValid():
			return QVariant()
		elif role == Qt.TextAlignmentRole:
			return QVariant(Qt.AlignRight | Qt.AlignVCenter)
		elif role == Qt.DisplayRole:
			column = index.column()
			player = self.players_index[index.row()][1]

			if column == 0:
				return QVariant(str(self.scores[player]["Nick"]))
			elif column == 1:
				if self.current_game in self.scores[player]["Games"]:
					return QVariant(str(self.scores[player]["Games"][self.current_game]["Best Score"]))
				else:
					return QVariant(str("---"))
		return QVariant()

	def load_scores_from_json(self, games_json):
		if os.path.isfile(games_json):
			with open(games_json) as f:
				try:
					self.beginResetModel()
					self.scores = json.load(f)
					self.players_index = list(enumerate(self.scores.keys()))
					self.endResetModel()
					# pprint(self.scores)
				except Exception as e:
					print "Error loading json file"
					print(e)
		else:
			try:
				json.loads(json)
			except:
				print "No json format"

	def get_available_games(self):
		available_games = []
		if len(self.scores) > 0:
			for player in self.scores.keys():
				for game in self.scores[player]["Games"].keys():
					if game not in available_games:
						available_games.append(game)
		return available_games



class QScoreBoard(QWidget):
	def __init__(self, parent=None):
		super(QScoreBoard, self).__init__(parent)
		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.view = QTableView()
		self.games_combo_layout = QHBoxLayout()
		self.games_combobox = QComboBox()
		self.model = QScoreBoardTableModel()
		self.model.load_scores_from_json('resources/scores.json')
		games = self.model.get_available_games()
		self.games_combobox.addItems(QStringList(games))
		self.view.setModel(self.model)
		# try some sorting
		self.view.setSortingEnabled(True)
		# allow drag to rearrange columns
		self.view.horizontalHeader().setMovable(True)

		self.main_layout.addWidget(self.view)
		self.games_combo_layout.addStretch()
		self.games_combo_layout.addWidget(self.games_combobox)
		self.main_layout.addLayout(self.games_combo_layout)




if __name__ == '__main__':
	app = QApplication(sys.argv)
	score_board = QScoreBoard()
	score_board.show()
	app.exec_()
