
from bbdd import *


if __name__ == '__main__':
    bbdd = BBDD()

    # create database
#    bbdd.create_database("prueba.db")
    #or open an existing one
    bbdd.open_database("prueba.db")


    #write
    in_pat = bbdd.new_patient('Andres', 'Lopez Lopez', 12)
    print in_pat

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
