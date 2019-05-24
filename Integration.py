
import csv
import os #os module imported here
import time
import shutil

current = r'/home/pi/Inzynierka/Dash_App/csv_memory//'
dash = r'/home/pi/Inzynierka/Dash_App/dash_csv//'
path = r'/home/pi/Inzynierka/Dash_App/csv_memory//'
moveto = r'/home/pi/Inzynierka/Dash_App/database//'
cycle = 0
NG = 0
OK = 0
x1=0

class Watcher:
    liczZ = 0
    """ A simple class, set to watch its variable. """
    def __init__(self, value):
        self.variable = value

    def set_value(self, new_value):
        if self.variable != new_value:
            self.variable = new_value
            self.post_change()
        return self.liczZ

    def post_change(self):
        global liczZ
        self.liczZ += 1
        return self.liczZ

class DataMove:

    state = True

    def __init__(self, state):
        self.state = state


    def move_to_directory(self, path, moveto):
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=False)
        k = 0
        try:
            if self.state !=False and files.__len__() > k:
                x = files[k]
                b = x.split('//')
                src = path + b[1]
                dst = moveto + b[1]
                shutil.move(src, dst)
                k += 1
                time.sleep(0.1)

        except FileNotFoundError:
            print('blad')



    def setState(self, newstate):
        self.state = newstate


def get_latest(folder):
    try:
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.csv')]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        if not files:
            return None
        else:
            return files[0]
    except FileNotFoundError:
        print('nie znaleziono pliku')


def file_to_analizes():
    try:
        time_sorted_list = get_latest(current)

        if time_sorted_list is None:
            plots = None
        else:
            csv_file = open(time_sorted_list)
            plots = csv.reader(csv_file, delimiter=';')
        return plots
    except IndexError:
        print("IndexError:")
    except FileNotFoundError:
        print("Brak Plików")


def File_Change1():
    global x1
    folder =r'/home/pi/Inzynierka/Dash_App/csv_memory/'
    try:
        x1 = len([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.csv')])
        return x1
    except FileNotFoundError:
        print('nie znaleziono pliku')
        return x1


def data_separate(plots):
    line_count = 0
    y = []
    for row in plots:
        if line_count < 10:
            line_count += 1
        elif line_count <13: #Data,czas
            y.append((row[1]))
            line_count += 1
        elif line_count == 15: #numer pomiaru
            y.append((row[1]))
            line_count += 1
        elif line_count == 17: #Nazwa
            y.append((row[1]))
            line_count += 1
        elif line_count < 30:
            line_count += 1
        elif line_count < 32: #ostatnia wartosc x,y
            y.append(float(row[1]))
            line_count += 1
        elif line_count == 34: #Peak
            y.append(float(row[1]))
            line_count += 1
        elif line_count == 37:  # Peak
            y.append(float(row[4]))
            line_count += 1
        elif line_count < 223:
            line_count += 1
        elif line_count < 225: #Granice pomiaru w dlugosci
            y.append((row[2]))
            line_count += 1
        elif line_count < 270:
            line_count += 1
        elif line_count == 270:  #Liczba pomiarow
            y.append((row[1]))
            line_count += 1
        else:
            line_count += 1
    return y


def Pomiar_sil(plots):
    max_force = float(data_separate(file_to_analizes())[8])
    max_force1=max_force*0.99
    line_count = 0
    row_count = 0
    stage1=0
    stage2=0
    z=0
    y = []
    x = []
    x1 = []
    y1 = []
    peak = 0
    for row in plots:
        if line_count <= 280:
            line_count += 1
            row_count += 1
        elif line_count > 280 and peak != 1:
                if z < max_force1:
                    z = round(float(row[2]),4)
                    y.append(z)

                    line_count += 1
                    row_count += 1
                    stage1 += 1
                    x.append(float(stage1))
                    # x.append(float(stage1))
                else:
                    peak=1
        elif row.__len__() > 2 and row[3] != '' and peak == 1 :
            g = round(float(row[2]), 4)
            y1.append(g)
            line_count += 1
            row_count += 1
            stage2 += 1
            x1.append(float(stage2))
            # x1.append(float(stage2))
    return x,y,x1,y1,max_force


def force_motion_value(plots):
    line_count = 0
    x = []
    y = []
    try:
        for row in plots:
            if line_count < 280:
                line_count += 1
            elif row.__len__() > 2 and row[3] != '':
                x.append(float(row[1]))
                y.append(float(row[2]))
                line_count += 1
    except TypeError:
        print('Brak plikow CSV')
    return x, y


def Delta_Force_Stage_1():
    strefa_1 = []
    strefa_2 = []
    strefa_11 = []
    strefa_22 = []
    stage1=0
    stage2=0
    change = 0
    przedzial = Pomiar_sil(file_to_analizes())[1]
    dzielnik = float(Pomiar_sil(file_to_analizes())[4])
    start_1 = float(data_separate(file_to_analizes())[11])
    zakres_I=start_1*0.15
    wychylenia1 = (dzielnik/(start_1*0.35))
    wychylenia2 = (dzielnik / (start_1 * 0.25))
    # print(dzielnik)
    # print(start_1)
    # print(wychylenia1)
    # print(wychylenia2)
    ostrze_I=0
    ostrze_II=0
    try:
        for w in range(len(przedzial)):
            if float(w) > 0:
                z = float(przedzial[w] - przedzial[w-1])
                round(z,4)
                if z < wychylenia1 and change != 1 or z >= wychylenia1 and stage1<=zakres_I:
                    strefa_1.append(float(round(z,4)))
                    stage1 += 1
                    strefa_11.append(float(stage1))
                    if abs(z) > 0.3*wychylenia1:
                        ostrze_I += 1
                elif z >= wychylenia1 and stage1>=zakres_I and change !=1:
                    change = 1
                elif change == 1:
                    strefa_2.append(float(round(z,4)))
                    stage2 += 1
                    strefa_22.append(float(stage2))
                    if abs(z) > 1.4*wychylenia2 or abs(z) < 0.7*wychylenia2:
                        ostrze_II += 1
        return strefa_1,strefa_11,strefa_2,strefa_22,ostrze_I, ostrze_II
    except IndexError:
        print('brak do przeliczenia liczb')
        return strefa_1,strefa_11,strefa_2,strefa_22,ostrze_I, ostrze_II


def Delta_Force_Stage_2():
    strefa_3 = []
    strefa_4 = []
    strefa_33 = []
    strefa_44 = []
    stage3=0
    stage4=0
    change = 0
    przedzial2 = Pomiar_sil(file_to_analizes())[3]
    dzielnik = float(Pomiar_sil(file_to_analizes())[4])
    start_2= float(data_separate(file_to_analizes())[11])
    zakres_I=start_2*0.05
    wychylenia4 = (dzielnik/(start_2*0.5))
    wychylenia3 = (dzielnik / (start_2 * 0.25))
    # print(dzielnik)
    # print(start_1)
    # print(wychylenia1)
    # print(wychylenia2)
    # print(wychylenia3)
    ostrze_III=0
    ostrze_IV=0
    try:
        for w in range(len(przedzial2)):
            if float(w) > 0:
                z = float(przedzial2[w] - przedzial2[w-1])
                round(z,4)
                if z >0 and stage3<=zakres_I or z<2 and change !=1:
                    strefa_3.append(float(round(z, 4)))
                    stage3 += 1
                    strefa_33.append(float(stage3))
                    if abs(z) > 2 * wychylenia3 :
                        ostrze_III += 1
                elif z>0 and stage3>=zakres_I and change != 1:
                    change = 1
                elif change == 1:
                    strefa_4.append(float(round(z,4)))
                    stage4 += 1
                    strefa_44.append(float(stage4))
                    if abs(z) > wychylenia4:
                        ostrze_IV += 1
        return strefa_3,strefa_33,strefa_4,strefa_44,ostrze_III, ostrze_IV
    except IndexError:
        print('brak do przeliczenia liczb')
        return strefa_3,strefa_33,strefa_4,strefa_44,ostrze_III, ostrze_IV


def Analiza_Stref_I():

    strefa_1=Delta_Force_Stage_1()[4]
    if strefa_1 < 5:
        waga = 3
    elif strefa_1 <25:
        waga = 2
    else:
        waga = 1
    return waga


def Analiza_Stref_II():

    strefa_2=Delta_Force_Stage_1()[5]
    if strefa_2 < 5:
        waga = 3
    elif strefa_2 <25:
        waga = 2
    else:
        waga = 1
    return waga


def Analiza_Stref_III():

    strefa_3=Delta_Force_Stage_2()[4]
    if strefa_3 < 5:
        waga = 3
    elif strefa_3 <15:
        waga = 2
    else:
        waga = 1
    return waga


def Analiza_Stref_IV():

    strefa_4=Delta_Force_Stage_2()[5]
    if strefa_4 <= 5:
        waga = 3
    elif strefa_4 <=10:
        waga = 2
    else:
        waga = 1

    return waga


def counter_cykli():
    global cycle
    cycle+=1
    return cycle

def wsk_suma():
    p1 = Analiza_Stref_I()
    p2 = Analiza_Stref_II()
    p3 = Analiza_Stref_III()
    p4 = Analiza_Stref_IV()
    suma = p1 + p2 + p3 + p4
    return suma


def Stan_Koncowy_Ostrza():
    global NG
    global OK
    suma=wsk_suma()
    if suma > 10:
        stan = 0
        OK += 1
    elif suma > 8:
        stan = 0
        OK += 1
    elif suma > 6:
        stan = 1
        NG += 1
    else:
        stan = 1
        NG += 1
    return stan



def wsk_OK():
    wskOK=(OK/cycle)*100
    new = int(round(wskOK))
    return new


def wsk_NG():
    wskNG=(NG/cycle)*100
    new = int(round(wskNG))
    return new


def csvwrite(x, y, ok, ng,stan):
    with open(r'/home/pi/Inzynierka/Dash_App/skrypt/test.csv', 'w',newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([x])  #OstrośćOstrza
        filewriter.writerow([y])  #NrCyklu
        filewriter.writerow([ok]) #wskOK
        filewriter.writerow([ng]) #wskNG
        filewriter.writerow([stan])  # stan
    csvfile.close()

if __name__ == '__main__':
    # Listener
    process_tester = DataMove(True)
    licznik = Watcher(File_Change1())
    beck=0
    counter = 0;
    while True:
        check = licznik.set_value(File_Change1())
        z = File_Change1()
        time.sleep(0.1)
        try:
            while check != beck and file_to_analizes() is not None and z > 1:

                counter = counter + 1
                print(counter)
                # wykonanie skryptu
                beck = licznik.set_value(File_Change1())
                file_to_analizes()
                csvwrite(Stan_Koncowy_Ostrza(),counter_cykli(),wsk_OK(),wsk_NG(),wsk_suma())
                if z > 1 and counter < 10:
                    process_tester.setState(True)
                    process_tester.move_to_directory(path, moveto)
                    process_tester.setState(False)
                    z=z-1
                elif counter >=10:
                    process_tester.setState(True)
                    process_tester.move_to_directory(path, dash)
                    process_tester.setState(False)
                    counter = 0
                print('cykle',cycle)

        except PermissionError:
            print('bład odczytu')
        except TypeError:
            print('bład odczytu')