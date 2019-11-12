#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QListWidgetItem, QVBoxLayout, QWidget, QDialog
from bbdd import *

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
UIS_FOLDER = os.path.join(CURRENT_FILE_PATH, "uis" )


class History(QDialog):
    bbdd = None
    patients = {}

    def __init__(self, bbdd, parent=None):
        super(History, self).__init__(parent)
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        self.bbdd = bbdd
        loader = QUiLoader()
        file = QFile(os.path.join(UIS_FOLDER, "history.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self.parent())
        self.mylayout.addWidget(self.ui)
        self.mylayout.setContentsMargins(0, 0, 0, 0)
        file.close()
        self.initialize()
        self.ui.paciente_lw.setCurrentRow(0)

    def initialize(self):
        # GUI connections
        self.ui.paciente_lw.itemSelectionChanged.connect(self.load_patient_info)
        self.ui.sesion_lw.itemSelectionChanged.connect(self.load_session_info)
        self.ui.juego_lw.itemSelectionChanged.connect(self.load_game_info)
        self.ui.close_btn.clicked.connect(self.close)
        # load data
        self.load_patients()

    def load_patients(self):
        pat_list = self.bbdd.get_all_patients()
        for pat in pat_list:
            item = QListWidgetItem(pat.username)
            item.setData(Qt.UserRole, pat)
            self.ui.paciente_lw.addItem(item)

    def load_patient_info(self):
        self.clear_patient_info()
        item = self.ui.paciente_lw.currentItem()
        patient = item.data(Qt.UserRole)
        self.ui.paciente_gb.setTitle("[" + patient.nombre + "] ")
        self.ui.p_sexo_le.setText(patient.sexo)
        self.ui.p_edad_le.setText(str(patient.edad))
        self.ui.p_ncog_le.setText(str(patient.nivelCognitivo))
        self.ui.p_nfisico_le.setText(str(patient.nivelFisico))
        self.ui.p_njuego_le.setText(str(patient.nivelJuego))
        self.ui.p_centro_le.setText(patient.centro)
        self.reload_sessions(patient.username)

    def clear_patient_info(self):
        self.ui.sesion_lw.clear()
        self.ui.paciente_gb.setTitle("[Paciente]")
        self.ui.p_sexo_le.clear()
        self.ui.p_edad_le.clear()
        self.ui.p_ncog_le.clear()
        self.ui.p_nfisico_le.clear()
        self.ui.p_njuego_le.clear()
        self.ui.p_centro_le.clear()

    def reload_sessions(self, username):
        self.clear_session_info()
        print("Reload sessions from patient: ", username)
        session_list = self.bbdd.get_all_session_by_patient_username(username)

        for session in session_list:
            item = QListWidgetItem(session.start_time.strftime("%d/%m/%Y"))
            item.setData(Qt.UserRole, session)
            self.ui.sesion_lw.addItem(item)

    def reload_rounds(self, session_id):
        ngames = 0
        win = 0
        lost = 0
        help = 0
        check = 0

        round_list = self.bbdd.get_all_round_by_session_id(session_id)
        for round in round_list:
            item = QListWidgetItem(round.name)
            item.setData(Qt.UserRole, round)
            self.ui.juego_lw.addItem(item)
            # compute global session values
            ngames += 1
            if round.result:
                win += 1
            else:
                lost += 1
            help += round.n_helps
            check += round.n_checks
        # update global session values
        self.ui.s_ngames_le.setText(str(ngames))
        self.ui.s_win_le.setText(str(win))
        self.ui.s_lost_le.setText(str(lost))
        self.ui.s_help_le.setText(str(help))
        self.ui.s_check_le.setText(str(check))

    def clear_session_info(self):
        self.clear_game_info()
        self.ui.juego_lw.clear()
        self.ui.sesion_gb.setTitle("[Sesión]")
        self.ui.s_time_le.clear()
        self.ui.s_ngames_le.clear()
        self.ui.s_win_le.clear()
        self.ui.s_lost_le.clear()
        self.ui.s_help_le.clear()
        self.ui.s_check_le.clear()

    def load_session_info(self):
        self.clear_session_info()
        item = self.ui.sesion_lw.currentItem()
        session = item.data(Qt.UserRole)
        self.ui.sesion_gb.setTitle("[" + session.start_time.strftime("%d/%m/%Y") + "]")
        total_time = (session.end_time - session.start_time)
        # TODO: look for a better way to format text than spliting
        self.ui.s_time_le.setText(str(total_time).split('.')[0])
        self.reload_rounds(session.id)

    def load_game_info(self):
        self.clear_game_info()
        item = self.ui.juego_lw.currentItem()
        game = item.data(Qt.UserRole)
        self.ui.juego_gb.setTitle("[" + game.name + "]")
        play_time = (game.end_time - game.start_time)
        self.ui.j_fecha_le.setText(game.start_time.strftime("%d/%m/%Y"))
        self.ui.j_ganado_le.setText("Sí" if game.result else "No")
        # TODO: look for a better way to format text than spliting
        self.ui.j_tjugado_le.setText(str(play_time).split('.')[0])
        self.ui.j_distancia_le.setText(str(game.distance))
        self.ui.j_ayudas_le.setText(str(game.n_helps))
        self.ui.j_comprobaciones_le.setText(str(game.n_checks))

    def clear_game_info(self):
        self.ui.juego_gb.setTitle("[Juego]")
        self.ui.j_fecha_le.clear()
        self.ui.j_ganado_le.clear()
        self.ui.j_tjugado_le.clear()
        self.ui.j_distancia_le.clear()
        self.ui.j_ayudas_le.clear()
        self.ui.j_comprobaciones_le.clear()

    def set_selected_patient(self, patient):
        found_patients = self.ui.paciente_lw.findItems(patient, Qt.MatchExactly)
        if len(found_patients)>0:
            self.ui.paciente_lw.setCurrentItem(found_patients[0])
            self.load_patient_info(found_patients[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    bbdd = BBDD()
    bbdd.open_database("/home/robolab/robocomp/components/euroage-tv/components/bbdd/prueba1.db")

    history = History(bbdd)
    history.show()

    sys.exit(app.exec_())
