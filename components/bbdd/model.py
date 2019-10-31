from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Sequence, ForeignKey, Text
from sqlalchemy.orm import relationship

Base = declarative_base()


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, Sequence('patient_id_seq'))
    username = Column(String(20), primary_key=True)
    nombre = Column(String(60))
    sexo = Column(String(20))
    edad = Column(Integer)
    datosRegistro = Column(Text())
    nivelCognitivo = Column(Integer)
    nivelFisico = Column(Integer)
    nivelJuego = Column(Integer)
    centro = Column(Integer)
    profesional = Column(String(20))
    observaciones = Column(Text())
    fechaAlta = Column(String(20))

    session = relationship("Session", back_populates="patient", cascade="all, delete")

    def __repr__(self):
        return "<Patient(username='%s' nombre=%s')>" % (self.username, self.nombre)


class Therapist(Base):
    __tablename__ = 'therapist'
    id = Column(Integer, Sequence('therapist_id_seq'))
    nombre = Column(String(60))
    username = Column(String(20), primary_key=True)
    hash = Column(String(100))
    salt = Column(String(50))
    centro = Column(Integer)
    telefono = Column(String(20))
    profesion = Column(String(30))
    observaciones = Column(Text)
    fechaAlta = Column(String(20))

    session = relationship("Session", back_populates="therapist", cascade="all, delete")

    def __repr__(self):
        if self.nombre is not None and self.username is not None:
            return "<Therapist(name='%s %s')>" % (self.nombre, self.username)
        else:
            return "<Therapist(name='None None')>"


class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, Sequence('game_id_seq'), primary_key=True)
    name = Column(String(50))
    ntiles = Column(Integer)

    rounds = relationship("Round", back_populates="game", cascade="all, delete")

    def __repr__(self):
        return "<Game(name='%s: %d')>" % (self.name, self.ntiles)


class Round(Base):
    __tablename__ = 'round'
    id = Column(Integer, Sequence('round_id_seq'), primary_key=True)
    name = Column(String(50))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    n_checks = Column(Integer)
    n_helps = Column(Integer)
    n_screen_touch = Column(Integer)
    distance = Column(Integer)
    result = Column(Boolean)
    session_id = Column(Integer, ForeignKey('session.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    hand_id = Column(Integer, ForeignKey('hand.id'))
    stop_id = Column(Integer, ForeignKey('stop.id'))


    game = relationship("Game", back_populates="rounds", cascade="all, delete")
    hand = relationship("Hand", back_populates="rounds", cascade="all, delete")
    stop = relationship("Stop", back_populates="rounds", cascade="all, delete")

    def __repr__(self):
        return "<Round(name='%s')>" % self.name


class Hand(Base):
    __tablename__ = 'hand'
    id = Column(Integer, Sequence('hand_id_seq'), primary_key=True)
    poses = Column(String(50))
    nopen = Column(Integer)
    nclose = Column(Integer)

    rounds = relationship("Round", back_populates="hand", cascade="all, delete")

    def __repr__(self):
        return "<Hand(id='%d')>" % self.id


class Game_State(Base):
    __tablename__ = 'game_state'
    id = Column(Integer, Sequence('game_state_id_seq'), primary_key=True)
    timestamp = Column(DateTime)
    nmoved_tiles = Column(Integer)
    ncorrect_tiles = Column(Integer)

    stop = relationship("Stop", back_populates="game_state", cascade="all, delete")

    def __repr__(self):
        return "<Game_state(id='%d')>" % self.id


class Stop(Base):
    __tablename__ = 'stop'
    id = Column(Integer, Sequence('stop_id_seq'), primary_key=True)
    time = Column(Integer)
    poseX = Column(Integer)
    poseY = Column(Integer)
    poseZ = Column(Integer)
    stop_id = Column(Integer, ForeignKey('stop.id'))
    game_state_id = Column(Integer, ForeignKey('game_state.id'))

    game_state = relationship("Game_State", back_populates="stop", cascade="all, delete")
    rounds = relationship("Round", back_populates="stop", cascade="all, delete")

    def __repr__(self):
        return "<Stop(id='%d')>" % self.id


class Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, Sequence('session_id_seq'), primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    patient_id = Column(Integer, ForeignKey('patient.username'))
    therapist_id = Column(Integer, ForeignKey('therapist.username'))

    patient = relationship("Patient", back_populates="session", cascade="all, delete")
    therapist = relationship("Therapist", back_populates="session", cascade="all, delete")

    def __repr__(self):
        if self.id is not None:
            return "<Session(id='%d')>" % self.id
        else:
            return "<Session(id = None)>"
