
from datetime import datetime

class Metrics():
    def __init__(self):
        self.game_start = ""
        self.game_end = ""
        self.time = 0
        self.session_start = ""
        self.session_end = ""
        self.distance = 0
        self.num_hand_open = 0
        self.num_screen_touched = 0
        self.num_hits= 0
        self.num_fails = 0
        self.num_help = 0


    def add_game(self,time,aciertos): #API BD
        pass

class Elderly():
    def __init__(self, n, s1,s2,age):
        self.name = n
        self.surname1 = s1
        self.surname2 = s2
        self.age = age
        self.game_metrics = {}


class Admin_Elderly():
    def __init__(self):
        self.list_elderly = {}
        self.id = 1

    def add_elderly(self,n,s1,s2,age): #comprobar que no exista previamente, que devuelva true o false

        id_person = self.id
        person = Elderly(n, s1, s2,age)
        self.list_elderly[id_person] = person
        self.id = self.id + 1
        return id_person

    def obtain_metrics (self,id):
        data = self.list_elderly[id]
        m = data.metrics
        print 'Partidas jugadas = ',m.games_played, ' - Media de tiempo empleado = ', m.average_time, ' - Media de victorias = ', m.average_win

    def get_list_elderly(self):
        list = []
        for id, data in self.list_elderly.items():
            player_name = str(id)+" "+data.name+" "+data.surname1+" "+data.surname2
            print (player_name)
            list.append(player_name)
            
        return list

if __name__ == '__main__':
    admin = Admin_Elderly()
    # admin.add_elderly("Juanito","Perez", "Fernandez",88)

    today = datetime.now()
    print today.strftime('We are the %c')

    print(today.strptime("Mon Mar 25 12:56:34 2019","%c"))


    # admin.get_list_elderly()
    # admin.obtain_metrics (1)