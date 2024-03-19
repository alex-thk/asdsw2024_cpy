# See "Distributed Systems" - Van Steen, Tanenbaum - Ed. 4 (p. 118)

from multiprocessing import Process
from threading import Thread
from time import *
from random import *


# dentro un thread possono esistere più linee di esecuzione in parallelo

# nei thread c'è condivisione dello spazio di memoria quindi si deve fare attenzione
def sleeping(name):
    global shared_x
    s = randint(1, 20)
    sleep(s)
    shared_x = shared_x + 1

    t = gmtime()
    s = randint(1, 20)
    txt = str(t.tm_min) + ':' + str(t.tm_sec) + ' ' + name + ' is going to sleep for ' + str(s) + ' seconds'
    print(txt)
    sleep(s)
    t = gmtime()
    txt = str(t.tm_min) + ':' + str(t.tm_sec) + ' ' + name + ' has woken up, seeing shared_x being ' + str(shared_x)
    print(txt)


def sleeper(name, num_thread):
    sleeplist = list()

    global shared_x  # variabile globale randomica che non viene aggiornato dai processi
    shared_x = randint(10, 99)

    for i in range(num_thread):
        subsleeper = Thread(target=sleeping, args=(name + ' ' + str(i),))
        sleeplist.append(subsleeper)

    txt = name + ' sees shared_x being ' + str(shared_x)
    print(txt)

    for s in sleeplist: s.start()
    for s in sleeplist: s.join()

    txt = name + ' sees shared_x being ' + str(shared_x)
    print(txt)


if __name__ == '__main__':

    # iloc programma principale genera 10 processi
    process_list = list()
    for i in range(10):
        process_list.append(Process(target=sleeper, args=('bob_' + str(i), randint(2, 4),)))
    # qui ho un mix di processi e thread, il main genera 10 processi (multiprocess) mentre ogni processo generato avrà 2-4 thread (multithread)
    # quindi processi non avranno memoria condivisa tra loro ma i thread sì
    global shared_x
    shared_x = randint(10, 99)
    # creando i processi dal programma principale, i processi ereditano le variabili e la memoria però avranno memorie non condivise
    print(shared_x)

    for p in process_list: p.start()

    for p in process_list: p.join()

    print(shared_x)
