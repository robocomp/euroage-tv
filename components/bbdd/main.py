
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import *


engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#create database
Base.metadata.create_all(engine)


ed_pat = Patient(name='Andres', surname='Lopez Lopez')
print ed_pat


#add
session.add(ed_pat)

session.commit()

#read
our_user = session.query(Patient).filter_by(name='Andres').first()
print our_user


# session.rollback()
# session.delete(jack)