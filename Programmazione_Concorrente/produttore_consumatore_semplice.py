from threading import Thread, Lock
import time
import logging
from random import randrange
from sys import argv

# mutual exclusion e serve affinchè i due thread si possano sincronizzare sulla struttura di dati condivisa. Facendo
# un acquire su un oggetto di tipo lock succede che: se nessun thread ha acquisito il mutex allora prendo il mutex e
# vado avanti altrimenti mi fermo e aspetto che il mutex venga rilasciato

# il mutex fa da sorta di controllore dell'area di memoria condivisa proteggendola.
# con strutture dati più complesse il meccanismo di mutua asclusione è fondamentale in quanto aiuta lo schedulatore
# a capire quale thread deve lavorare su una certa area di memoria condivisa
mutex = Lock()
sharedBuffer = []
produttoreRunning = True


def thread_produttore(nome, nomefile):
    # accesso alle variabili globali
    global sharedBuffer
    global mutex
    global produttoreRunning

    logging.info("{} sta partendo ...".format(nome))
    # logging.info("%s sta partendo ...", nome)

    with open(nomefile, 'r') as f:
        row = f.readline()
        while row:
            mutex.acquire()
            sharedBuffer.append(row[:-1])
            mutex.release()
            time.sleep(randrange(2))
            row = f.readline()

    produttoreRunning = False
    logging.info("{} sta terminando ...".format(nome))


def thread_consumatore(nome):
    global sharedBuffer
    global mutex
    global produttoreRunning

    logging.info("{} sta partendo ...".format(nome))
    # fin quando il produttore è attivo o fin quando c'è materiale sul buffer
    # il consumatore continua a lavorare
    while produttoreRunning or len(sharedBuffer) > 0:
        if len(sharedBuffer) > 0:
            mutex.acquire()
            row = sharedBuffer[0]
            logging.info("{} ha letto dalla memoria condivisa la riga [{}]".format(nome, row))
            sharedBuffer.remove(row)
            mutex.release()
        else:
            time.sleep(randrange(2, 5))

    logging.info("{} sta terminando ...".format(nome))


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main       :  before creating threads")

    # generazione di 2 thread
    produttore = Thread(target=thread_produttore, args=('Produttore', argv[1],))
    consumatore = Thread(target=thread_consumatore, args=('Consumatore',))

    logging.info("Main       :  before running threads")

    produttore.start()
    consumatore.start()

    logging.info("Main       :  wait for the threads to finish")

    produttore.join()
    consumatore.join()

    logging.info("Main       :  all done")
