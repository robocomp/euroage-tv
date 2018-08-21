#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from PyQt4.QtCore import QAbstractTableModel, QString, Qt, QVariant
from PyQt4.QtGui import QApplication, QTableView


class QScoreBoardTableModel(QAbstractTableModel):
	def __init__(self, parent=None):
		super(QScoreBoardTableModel, self).__init__(parent)
		self.t = []

	def rowCount(self, index=None):
		return 2

	def columnCount(self, index=None):
		return 3

	def data(self, index, role=None):
		if role == Qt.DisplayRole:
			return QString("Row:%d, Column:%d"%(index.row()+1, index.column()+1))
		return QVariant()

	def load_scores_from_json(self, json):
		if os.path.isfile(json):
			with open(json) as f:
				self.scores = json.load(f)
		else:
			try:
				json.loads(json)
			except:
				print "No json format"


class QScoreBoardView(QTableView):
	def __init__(self, parent=None):
		super(QScoreBoardView, self).__init__(parent)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	model = QScoreBoardTableModel()
	view = QScoreBoardView()
	view.setModel(model)
	view.show()
	app.exec_()
