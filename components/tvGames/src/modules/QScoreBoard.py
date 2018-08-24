#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time

from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant, QStringList
from PyQt4.QtGui import QApplication, QTableView, QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QHeaderView

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
		self.current_game = ""
		self.headers = []

	def rowCount(self, index=None):
		return len(self.scores)

	def columnCount(self, index=None):
		return len(self.headers)

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
			else:
				if self.current_game in self.scores[player]["Games"]:
					header = self.headers[column]
					value = self.scores[player]["Games"][self.current_game][header]
					if header == "Last time":
						value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(value)))
					if header == "Seconds played":
						seconds = abs(int(value))
						format_string = u""
						time_values = []
						s= seconds
						if seconds > 31557600:
							format_string += u"%d años "
							years, seconds = divmod(seconds, 31557600)
							time_values.append(years)
						if seconds > 604800:
							format_string += u"%d semanas "
							weeks, seconds = divmod(seconds, 604800)
							time_values.append(weeks)
						if seconds > 86400:
							format_string += u"%d dias "
							days, seconds = divmod(seconds, 86400)
							time_values.append(days)
						if seconds>3600:
							format_string += u"%d horas "
							hours, seconds = divmod(seconds, 3600)
							time_values.append(hours)
						if seconds > 60:
							format_string += u"%d min "
							minutes, seconds = divmod(seconds, 60)
							time_values.append(minutes)

						format_string += u"%d seg"
						time_values.append(seconds)

						# time_delta = datetime.timedelta(seconds=666)
						# format_string =  u"%S seg"
						# if int(value) > 60:
						# 	format_string =  u"%M min "+format_string
						# if int(value) > 3600:
						# 	format_string = u"%H horas " + format_string
						# if int(value) > 86400:
						# 	format_string = u"%D dias " + format_string
						# # if int(value) > 2629746:
						# # 	format_string = u"% días " + format_string
						# if int(value) > 31557600:
						# 	format_string = u"%Y anos " + format_string
						value = str(format_string%tuple(time_values))
						# value = time.strftime(format_string, time.gmtime(int(value)))
					return QVariant(str(value))
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
					self.get_headers_from_scores()
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
		available_games = ["---"]
		if len(self.scores) > 0:
			for player in self.scores.keys():
				for game in self.scores[player]["Games"].keys():
					if game not in available_games:
						available_games.append(game)
		return available_games

	def get_headers_from_scores(self):
		self.headers = ["Nick"]
		other_headers = []
		if len(self.scores) > 0:
			for player in self.scores.keys():
				for game in self.scores[player]["Games"].keys():
					for header in self.scores[player]["Games"][game].keys():
						if header not in other_headers:
							other_headers.append(header)
		self.headers.extend(sorted(other_headers))

	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return QVariant(self.headers[col])
		return QVariant()

	def set_current_game(self, game_name):
		self.beginResetModel()
		self.current_game = game_name
		self.endResetModel()



class QScoreBoard(QWidget):
	def __init__(self, parent=None):
		super(QScoreBoard, self).__init__(parent)
		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)
		self.view = QTableView()
		self.view.horizontalHeader().setResizeMode(QHeaderView.Stretch)
		self.games_combo_layout = QHBoxLayout()
		self.games_combobox = QComboBox()
		self.model = QScoreBoardTableModel()
		self.model.load_scores_from_json('resources/scores.json')
		games = self.model.get_available_games()
		self.games_combobox.addItems(QStringList(games))
		self.games_combobox.currentIndexChanged.connect(self.current_game_changed)
		self.view.setModel(self.model)
		# try some sorting
		self.view.setSortingEnabled(True)
		# allow drag to rearrange columns
		self.view.horizontalHeader().setMovable(True)

		self.main_layout.addWidget(self.view)
		self.games_combo_layout.addStretch()
		self.games_combo_layout.addWidget(self.games_combobox)
		self.main_layout.addLayout(self.games_combo_layout)

	def current_game_changed(self, qt_string):
		current_game = unicode(self.games_combobox.currentText())
		self.model.set_current_game(current_game)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	score_board = QScoreBoard()
	score_board.show()
	app.exec_()
