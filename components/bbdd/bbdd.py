from __future__ import print_function

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

from model import *


class BBDD(object):
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
    def new_patient(self, username, nombre, sexo="", edad=0, datosRegistro="", nivelCognitivo=0, nivelFisico=0, nivelJuego=0, centro="", profesional="", observaciones="", fechaAlta=None):
        if fechaAlta is None:
            fechaAlta = datetime.date.today().strftime("%Y %m %d")
        patient = Patient(username= username, nombre=nombre, sexo=sexo, edad=edad, datosRegistro=datosRegistro,
                          nivelCognitivo=nivelCognitivo, nivelFisico=nivelFisico, nivelJuego=nivelJuego, centro=centro,
                          profesional=profesional, observaciones=observaciones, fechaAlta=fechaAlta)
        try:
            self.session.add(patient)
            self.session.commit()
            return True, patient
        except Exception as e:
            self.session.rollback()
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Patient()

    def get_patient_by_name(self, name):
        try:
            return True, self.session.query(Patient).filter_by(name=name).first()
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Patient()

    def get_patient_by_username(self, username):
        try:
            return True, self.session.query(Patient).filter_by(username=username).first()
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Patient()

    def get_all_patients(self):
        return self.session.query(Patient).all()

    def remove_patient(self, username):
        ret, pat = self.get_patient_by_username(username)
        if ret:
            self.session.delete(pat)
            return True
        else:
            print("Patient: ", username, " not found in database")
            return False

    # THERAPIST
    def new_therapist(self, nombre, username, hash, salt, centro, telefono="", profesion="", observaciones="", fechaAlta=None):
        if fechaAlta is None:
            fechaAlta = datetime.date.today().strftime("%Y %m %d")
        therapist = Therapist( nombre=nombre, username=username, hash=hash, salt=salt, centro=centro, telefono=telefono,
                               profesion=profesion, observaciones=observaciones, fechaAlta=fechaAlta)
        try:
            self.session.add(therapist)
            self.session.commit()
            return True, therapist
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            self.session.rollback()
            return False, Therapist()

    def get_therapist_by_name(self, name):
        try:
            return True, self.session.query(Therapist).filter_by(name=name).first()
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Therapist()
        
    def get_therapist_by_username(self, username):
        try:
            return True, self.session.query(Therapist).filter_by(username=username).first()
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Therapist()

    def get_all_therapist(self):
        return self.session.query(Therapist).all()

    def remove_therapist(self, name):
        ret, ther = self.get_therapist_by_name(name)
        if ret:
            self.session.delete(ther)
            return True
        else:
            print("Therapist: ", name, " not found in database")
            return False

    # GAME
    def new_game(self, name, ntiles):
        game = Game(name=name, ntiles=ntiles)
        try:
            self.session.add(game)
            self.session.commit()
            return True, game
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Game()
    
    def get_game_by_name(self, name):
        try:
            return True, self.session.query(Game).filter_by(name=name).first()
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Game()

    def get_all_games(self):
        return self.session.query(Game).all()

    #GAME_STATE
    def new_game_state(self, time, nmoved_tiles, ncorrect_tiles):
        game_state = Game_State(start_time=time, nmoved_tiles=nmoved_tiles,ncorrect_tiles=ncorrect_tiles)
        try:
            self.session.add(game_state)
            self.session.commit()
            return True, game_state
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Game_state()

    # SESSION
    def new_session(self, start, end, patient, therapist):
        session = Session(start_time=start, end_time=end, patient_id=patient, therapist_id=therapist)
        try:
            self.session.add(session)
            self.session.commit()
            self.session.flush()
            # self.session.refresh()
            return True, session
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc()
            return False, Session()

    def get_all_session_by_therapist_username(self, username):
        result = self.session.query(Session).filter(Therapist.username == username).all()
        return result

    def get_all_session_by_patient_id(self, id):
        return self.session.query(Session).join(Patient).filter(Patient.id == id).all()

    def get_all_session_by_patient_username(self, username):
        return self.session.query(Session).join(Patient).filter(Patient.username == username).all()

    def get_session_by_id(self, id):
        return self.session.query(Session).filter_by(id=id).first()

    #HAND
    def new_hand(self, poses, nopen, nclose):
        hand = Hand(poses=poses, nopen=nopen, nclose=nclose)
        try:
            self.session.add(hand)
            self.session.commit()
            return True, hand
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Hand()

    #STOP
    def new_stop(self, time, poseX, poseY, poseZ, open_hand, tile, round_id, game_state_id):
        stop = Stop(time=time, poseX=poseX, poseY=poseY, poseZ=poseZ, open_hand=open_hand, tile=tile, round_id=round_id,
                    game_state_id=game_state_id)
        try:
            self.session.add(stop)
            self.session.commit()
            return True, stop
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Stop()

    #ROUND
    def new_round(self, name, stime, etime, nwins, nhelps, ntouch, result, game_id, hand_id, session_id):
        round = Round(name=name,start_time=stime, end_time=etime, n_checks=nwins, n_helps=nhelps, n_screen_touch=ntouch,
                      result=result,game_id=game_id, hand_id=hand_id, session_id=session_id)
        
        try:
            self.session.add(round)
            self.session.commit()
            return True, round
        except Exception as e:
            traceback.print_stack()
            traceback.print_exc(e)
            return False, Round()

    def get_all_round_by_session_id(self, id):
        return self.session.query(Round).join(Session).filter(Session.id == id).all()
