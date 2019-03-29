
from bbdd import *
from datetime import datetime

if __name__ == '__main__':
    bbdd = BBDD()

    # create database
    bbdd.create_database("prueba.db")
    #or open an existing one
#    bbdd.open_database("prueba.db")


    #write
    result, patient = bbdd.new_patient('Andres', 'Lopez Lopez')
    print patient
    result, patient2 = bbdd.new_patient('Elena', 'Martinez')
    print patient2

    #read
    result, out_pat = bbdd.get_patient_by_name('Andres')
    print result, out_pat

    #delete
    result = bbdd.remove_patient("Andres")
    print "Delete Andres", result

    #read all
    pat_list = bbdd.get_all_patients()
    print "All patients"
    for pat in pat_list:
        print pat

    #therapist
    result, therapist = bbdd.new_therapist("Luis", "Perez")

    #game
    game = bbdd.new_game("Ordenar tortilla", 5)

    #session
    time = datetime.now()
    result, session = bbdd.new_session(time, time, patient, therapist)
    print session

    time = datetime.now()
    result, session = bbdd.new_session(time, time, patient2, therapist)


    #get all session from therapist
    session_list = bbdd.get_all_session_by_therapist_name("Luis")
    print "All session from Luis"
    for s in session_list:
        print s

