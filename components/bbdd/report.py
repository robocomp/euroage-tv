import sys
from bbdd import *
from datetime import datetime
import dateutil.relativedelta
from fpdf import FPDF


from PySide2.QtWidgets import QApplication, QTableWidgetItem, QFileDialog, QMessageBox
from PySide2.QtCore import QDate


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
        self.ui.edate_de.setDate(datetime.today())
        self.ui.sdate_de.setDate(datetime.today() - dateutil.relativedelta.relativedelta(months=1))
        self.ui.cancel_pb.clicked.connect(self.cancel_pb)
        self.ui.generate_pb.clicked.connect(self.generate_report)
        self.ui.patient_cb.currentIndexChanged.connect(self.reload_sessions)
        self.ui.edate_de.dateChanged.connect(self.reload_sessions)
        self.ui.sdate_de.dateChanged.connect(self.reload_sessions)
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

    def reload_sessions(self):
        print "Reload sessions"
        patient_id = self.patients[self.ui.patient_cb.currentText()]
        session_list = self.bbdd.get_all_session_by_patient_id(patient_id)
        self.ui.sessions_tw.setRowCount(0)
        for session in session_list:
            if QDate(session.start_time) > self.ui.sdate_de.date() and QDate(session.start_time) < self.ui.edate_de.date():
                self.ui.sessions_tw.insertRow(self.ui.sessions_tw.rowCount())
                self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 0, QTableWidgetItem(str(session.id)))
                therapist = session.therapist.name + " " + session.therapist.surname
                self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 1, QTableWidgetItem(therapist))
                self.ui.sessions_tw.setItem(self.ui.sessions_tw.rowCount()-1, 2, QTableWidgetItem(session.start_time.strftime("%d/%m/%Y, %H:%M:%S")))

    def cancel_pb(self, event):
        print "cancel button"
        self.close()

    def generate_report(self):
        print "generate report",
        if self.ui.sessions_tw.currentRow() == -1:
            QMessageBox.information(self, ' ', 'Debe seleccionar una sesion para generar un informe')
            return
        filename = QFileDialog.getSaveFileName(self, 'Generate report', '', selectedFilter='*.pdf')[0]
        print filename
        if not filename:
            return
        session = self.bbdd.get_session_by_id(int(self.ui.sessions_tw.item(self.ui.sessions_tw.currentRow(), 0).text()))
        # create pdf
        pdf = FPDF()
        pdf.add_page()

        # Add header
        pdf.set_font("Arial", "B", size=20)
        pdf.cell(200, 20, txt="Informe de paciente", ln=1, align="C")

        # date_time
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(45, 8, txt="Fecha informe:")
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 8, txt=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), ln=1)
        pdf.ln()
        # paciente
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(25, 10, txt="PACIENTE:", ln=1)
        pdf.cell(25, 8, txt="Nombre:")
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 8, txt=session.patient.name, ln=1)
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(25, 8, txt="Apellido:")
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 8, txt=session.patient.surname, ln=1)
        pdf.ln()

        # session
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
        pdf.cell(0, 8, txt=session.therapist.name + " " + session.therapist.surname, ln=1)
        pdf.ln()

        # juego
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(25, 10, txt="JUEGO:", ln=1)

        # end pdf
        if '.pdf' not in filename:
            filename += '.pdf'
        pdf.output(filename)
        QMessageBox.information(self, ' ', 'Informe generado correctamente')


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
