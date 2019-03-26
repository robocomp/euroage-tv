from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import *


class BBDD():
    engine = None
    session = None

    # create database, initialize tables and open new connection
    def create_database(self, filename):
        self.open_database(filename)
        # create database
        Base.metadata.create_all(self.engine)

    def open_database(self, filename):
        if '.db' not in filename:
            filename += '.db'
        self.engine = create_engine('sqlite:///' + filename, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_database(self):
        self.session.close()

    #PATIENT
    def new_patient(self, name, surname, april):
        patient = Patient(name=name, surname=surname, id_april=april)
        self.session.add(patient)
        self.session.commit()
        return True, patient

    def get_patient_by_name(self, name):
        try:
            return True, self.session.query(Patient).filter_by(name=name).first()
        except:
            return False, Patient()

    def get_all_patients(self):
        return self.session.query(Patient).all()

    def remove_patient(self, name):
        ret, pat = self.get_patient_by_name(name)
        if ret:
            self.session.delete(pat)
            return True
        else:
            print "Patient: ", name, " not found in database"
            return False

    # THERAPIST
    def new_therapist(self, name, surname):
        therapist = Therapist(name=name, surname=surname)
        self.session.add(therapist)
        self.session.commit()
        return True, therapist

    def get_therapist_by_name(self, name):
        try:
            return True, self.session.query(Therapist).filter_by(name=name).first()
        except:
            return False, Therapist()

    def get_all_therapist(self):
        return self.session.query(Therapist).all()

    def remove_therapist(self, name):
        ret, ther = self.get_therapist_by_name(name)
        if ret:
            self.session.delete(ther)
            return True
        else:
            print "Therapist: ", name, " not found in database"
            return False
