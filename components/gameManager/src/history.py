import sys
from bbdd import *
from datetime import datetime
import dateutil.relativedelta


from PySide2.QtWidgets import QApplication, QTableWidgetItem, QListWidgetItem
from PySide2.QtCore import QDate, Qt


try:
    from ui_history import *
except:
    print ("Can't import UI file. Did you run 'make'?")
    sys.exit(-1)


class History(QtWidgets.QWidget):
    bbdd = None
    patients = {}

    def __init__(self, bbdd, parent=None):
        super(History, self).__init__(parent)
        self.bbdd = bbdd
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initialize()
        self.show()

    def initialize(self):
        # GUI connections
        self.ui.paciente_lw.itemClicked.connect(self.load_patient_info)
        self.ui.sesion_lw.itemClicked.connect(self.load_session_info)
        self.ui.juego_lw.itemClicked.connect(self.load_game_info)
        # load data
        self.load_patients()

    def load_patients(self):
        pat_list = self.bbdd.get_all_patients()
        for pat in pat_list:
            item = QListWidgetItem(pat.username)
            item.setData(Qt.UserRole, pat)
            self.ui.paciente_lw.addItem(item)

    def load_patient_info(self, item):
        self.clear_patient_info()
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

    def load_session_info(self, item):
        self.clear_session_info()
        session = item.data(Qt.UserRole)
        self.ui.sesion_gb.setTitle("[" + session.start_time.strftime("%d/%m/%Y") + "]")
        total_time = (session.end_time - session.start_time)
        self.ui.s_time_le.setText(str(total_time))
        self.reload_rounds(session.id)

    def load_game_info(self, item):
        self.clear_game_info()
        game = item.data(Qt.UserRole)
        self.ui.juego_gb.setTitle("[" + game.name + "]")
        play_time = (game.end_time - game.start_time)
        self.ui.j_fecha_le.setText(game.start_time.strftime("%d/%m/%Y"))
        self.ui.j_ganado_le.setText("Sí" if game.result else "No")
        self.ui.j_tjugado_le.setText(str(play_time))
        self.ui.j_tpausado_le.setText("")
        self.ui.j_ayudas_le.setText(str(game.n_helps))
        self.ui.j_comprobaciones_le.setText(str(game.n_checks))

    def clear_game_info(self):
        self.ui.juego_gb.setTitle("[Juego]")
        self.ui.j_fecha_le.clear()
        self.ui.j_ganado_le.clear()
        self.ui.j_tjugado_le.clear()
        self.ui.j_tpausado_le.clear()
        self.ui.j_ayudas_le.clear()
        self.ui.j_comprobaciones_le.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bbdd = BBDD()
    bbdd.open_database("prueba1.db")

    history = History(bbdd)

    sys.exit(app.exec_())
