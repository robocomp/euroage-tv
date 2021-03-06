from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, Sequence('patient_id_seq'), primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))

    session = relationship("Session", back_populates="patient", cascade="all, delete")

    def __repr__(self):
        return "<Patient(name='%s %s')>" % (self.name, self.surname)


class Therapist(Base):
    __tablename__ = 'therapist'
    id = Column(Integer, Sequence('therapist_id_seq'), primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))

    session = relationship("Session", back_populates="therapist", cascade="all, delete")

    def __repr__(self):
        return "<Therapist(name='%s %s')>" % (self.name, self.surname)


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
    n_wins = Column(Integer)
    n_helps = Column(Integer)
    n_screen_touch = Column(Integer)
    result = Column(Boolean)
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
    patient_id = Column(Integer, ForeignKey('patient.id'))
    therapist_id = Column(Integer, ForeignKey('therapist.id'))

    patient = relationship("Patient", back_populates="session", cascade="all, delete")
    therapist = relationship("Therapist", back_populates="session", cascade="all, delete")

    def __repr__(self):
        return "<Session(id='%d')>" % self.id
