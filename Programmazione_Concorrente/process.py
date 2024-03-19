# See "Distributed Systems" - Van Steen, Tanenbaum - Ed. 4 (p. 117)

from multiprocessing import Process  # è una libreria che serve a creare un processo a partire da quello attuale
from time import *
from random import *

global value

# NB tutti i processi in programmazione multiprocesso hanno memorie diverse che non c'entrano tra loro cosa che non
# avviene con la programmazione multithread. Questo non è un vantaggio perchè se devo condividere risorse tra processi
# allora nella programmazione multiprocesso dovrei usare altre risorse per far condividere le risorse tra i processi.
def sleeper(name): # rappresenta un processo che dorme per un tempo casuale e poi si sveglia
    global value
    t = gmtime()
    s = randint(4,20)
    txt = str(t.tm_min) + ':' + str(t.tm_sec) + ' ' + name + ' is going to sleep for ' + str(s) + ' seconds '
    #+ str(value)
    print(txt)
    sleep(s)
    t = gmtime()
    txt = str(t.tm_min) + ':' + str(t.tm_sec) + ' ' + name + ' has woken up '
    #+ str(value)
    print(txt)

if __name__ == '__main__':
    process_list = list()
    global value
    for i in range(10):
        p = Process(target=sleeper, args=('mike_{}'.format(i),))
        process_list.append(p)

    print('tutti i processi sono pronti')
    # non è detto che il primo programma che parte sia il primo a finire
    for i, p in enumerate(process_list):
        #value = i
        p.start()
        sleep(0.1) # se togliessi lo sleep 0.1 tutti i processi partirebbero contemporaneamente. Addirittura lo schedulatore
        # entra in gioco prima che il processo di stampa finisca, ecco perchè potrebbero risultare le stringhe in disordine

    print('tutti avviati')

    for p in process_list: p.join()     # p.join() è una sorta di cancello che fa si che il programma principale aspetti
                                        # che tutti i processi siano terminati

    print('tutti terminati!')
