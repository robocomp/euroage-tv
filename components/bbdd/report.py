import sys
from bbdd import *
from datetime import datetime
from fpdf import FPDF

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QTableWidgetItem
from PySide2.QtCore import QFile, QObject
from PySide2 import QtCore


try:
    from ui_report import *
except:
    print "Can't import UI file. Did you run 'make'?"
    sys.exit(-1)


class Report(QtWidgets.QWidget):
    bbdd = None
    patients = {}

    def __init__(self, bbdd, parent=None):
        super(Report, self).__init__(parent)
        self.bbdd = bbdd
        self.ui = Ui_Report()
        self.ui.setupUi(self)
        self.initialize()
        self.show()

    def initialize(self):
        self.ui.cancel_pb.clicked.connect(self.cancel_pb)
        self.ui.generate_pb.clicked.connect(self.generate_report)
        self.ui.patient_cb.currentIndexChanged.connect(self.change_patient)
        self.ui.sessions_tw.setColumnCount(3)
        self.ui.sessions_tw.setHorizontalHeaderLabels(["Id", "Therapist", "Date"])
        header = self.ui.sessions_tw.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignHCenter)
        header.setStretchLastSection(True)

    def load_patients(self):
        pat_list = self.bbdd.get_all_patients()
        name_list = []
        for pat in pat_list:
            name_list.append(pat.surname + " " + pat.name)
            self.patients[pat.surname + " " + pat.name] = pat.id
        name_list.sort()
        self.ui.patient_cb.addItems(name_list)

    def change_patient(self):
        print "change patient"
        patient_id = self.patients[self.ui.patient_cb.currentText()]
        session_list = self.bbdd.get_all_session_by_patient_id(patient_id)
        for session in session_list:
            self.ui.sessions_tw.insertRow(self.ui.sessions_tw.rowCount())
            self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 0, QTableWidgetItem(str(session.id)))
            therapist = session.therapist.name + " " + session.therapist.surname
            self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 1, QTableWidgetItem(therapist))
            self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 2, QTableWidgetItem(session.start_time.strftime("%d/%m/%Y, %H:%M:%S")))


    def filter_patient_sessions(self):
        print "change sessions"

    def cancel_pb(self, event):
        print "cancel button"
        self.close()

    def generate_report(self):
        print "generate report"

def add_image(image_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(image_path, x=10, y=8, w=100)
    pdf.set_font("Arial", size=12)
    pdf.ln(85)  # move 85 down
    pdf.cell(200, 10, txt="{}".format(image_path), ln=1)
    pdf.output("add_image.pdf")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    bbdd = BBDD()
    bbdd.open_database("prueba.db")

    report = Report(bbdd)
    report.load_patients()


    sys.exit(app.exec_())


    #create pdf
    pdf = FPDF()
    pdf.add_page()

    #Add header
    pdf.set_font("Arial","B", size=20)
    pdf.cell(200, 20, txt="Informe de paciente", ln=1, align="C")

    #date_time
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(45, 8, txt="Fecha informe:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), ln=1)
    pdf.ln()
    #paciente
    result, patient = bbdd.get_patient_by_name('Andres')
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(25, 10, txt="PACIENTE:", ln=1)
    pdf.cell(25, 8, txt="Nombre:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=patient.name, ln=1)
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(25, 8, txt="Apellido:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=patient.surname, ln=1)
    pdf.ln()

    #session
    session = bbdd.get_session_by_date(datetime.now())
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(25, 10, txt="SESION:", ln=1)
    pdf.cell(35, 8, txt="Fecha inicio:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=session.start_time.strftime("%d/%m/%Y, %H:%M:%S"), ln=1)
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(35, 8, txt="Fecha fin:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=session.end_time.strftime("%d/%m/%Y, %H:%M:%S"), ln=1)
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(35, 8, txt="Terapeuta:")
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 8, txt=session.therapist.name+" "+session.therapist.surname, ln=1)
    pdf.ln()

    #juego
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(25, 10, txt="JUEGO:", ln=1)

    #end pdf
    pdf.output("simple_demo.pdf")


    sys.exit(app.exec_())

