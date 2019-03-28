# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'report.ui',
# licensing of 'report.ui' applies.
#
# Created: Thu Mar 28 18:26:44 2019
#      by: pyside2-uic  running on PySide2 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Report(object):
    def setupUi(self, Report):
        Report.setObjectName("Report")
        Report.resize(605, 457)
        self.verticalLayout = QtWidgets.QVBoxLayout(Report)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Report)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.patient_cb = QtWidgets.QComboBox(Report)
        self.patient_cb.setEditable(False)
        self.patient_cb.setObjectName("patient_cb")
        self.horizontalLayout_2.addWidget(self.patient_cb)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Report)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.sdate_de = QtWidgets.QDateEdit(Report)
        self.sdate_de.setDateTime(QtCore.QDateTime(QtCore.QDate(2019, 3, 1), QtCore.QTime(0, 0, 0)))
        self.sdate_de.setCalendarPopup(True)
        self.sdate_de.setObjectName("sdate_de")
        self.horizontalLayout_3.addWidget(self.sdate_de)
        self.label_4 = QtWidgets.QLabel(Report)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.edate_de = QtWidgets.QDateEdit(Report)
        self.edate_de.setDateTime(QtCore.QDateTime(QtCore.QDate(2019, 4, 1), QtCore.QTime(0, 0, 0)))
        self.edate_de.setCalendarPopup(True)
        self.edate_de.setObjectName("edate_de")
        self.horizontalLayout_3.addWidget(self.edate_de)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(Report)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.sessions_tw = QtWidgets.QTableWidget(Report)
        self.sessions_tw.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.sessions_tw.setObjectName("sessions_tw")
        self.sessions_tw.setColumnCount(0)
        self.sessions_tw.setRowCount(0)
        self.verticalLayout.addWidget(self.sessions_tw)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.cancel_pb = QtWidgets.QPushButton(Report)
        self.cancel_pb.setObjectName("cancel_pb")
        self.horizontalLayout.addWidget(self.cancel_pb)
        self.generate_pb = QtWidgets.QPushButton(Report)
        self.generate_pb.setObjectName("generate_pb")
        self.horizontalLayout.addWidget(self.generate_pb)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Report)
        QtCore.QMetaObject.connectSlotsByName(Report)

    def retranslateUi(self, Report):
        Report.setWindowTitle(QtWidgets.QApplication.translate("Report", "Generate report", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Report", "Patient", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Report", "Start Date", None, -1))
        self.sdate_de.setDisplayFormat(QtWidgets.QApplication.translate("Report", "dd/MM/yyyy", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Report", "End Date", None, -1))
        self.edate_de.setDisplayFormat(QtWidgets.QApplication.translate("Report", "dd/MM/yyyy", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Report", "Sessions", None, -1))
        self.cancel_pb.setText(QtWidgets.QApplication.translate("Report", "Cancel", None, -1))
        self.generate_pb.setText(QtWidgets.QApplication.translate("Report", "Generate", None, -1))

