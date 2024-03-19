import socket
from sys import argv
import re
from threading import Thread, Lock


# tipicamente un server accetta le connessioni e poi viene diviso in thread dove un thread gestisce la connessione
# appena stabilita e un altro thread torna per gestisce la connessione successiva

def connection_manager_thread(addr, conn):
    print('Client: {}'.format(addr))
    toggle = True
    while True:
        data = conn.recv(1024)
        # NB il TCP è una sorta di buffer quindi una volta arrivato ad una sorta di limite di byte, nel nostro caso,
        # 1024 byte, il buffer si svuota e si può leggere di nuovo.
        if not data:
            break
        # in questo caso se toggle rimane True vuol dire che il mio server risponde sempre con un echo al client. Se da
        # il client da come input [TOGGLE] allora toggle diventa False e il server non risponde più con un echo al
        # client.
        if bool(re.search('^\[STOP\]', data.decode('utf-8'))):
            break
        if bool(re.search('^\[TOGGLE\]', data.decode('utf-8'))):
            toggle = not toggle
        print('{}: echo message: {}'.format(addr, data[:-1].decode('utf-8')))
        if toggle:
            conn.sendall(data)
    conn.close()


if __name__ == '__main__':

    localIP = argv[1]
    localPORT = int(argv[2])

    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPORT))

    while True:
        print('TCP Server UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
        TCPServerSocket.listen()
        conn, addr = TCPServerSocket.accept()
        # qui vengono create conn e addr che sono variabili locali (però che sono
        # in una zona di memoria condivisa)
        # conn e addr sono puntatori che puntano a valori nell'heap (zona dinamica di memoria)
        # il thread principale una volta che accetta una nuova connessione SOVRASCRIVE I PUNTATORI ADDR E CONN che però
        # sono memorizzati dal thread che sta gestendo quella connessione.

        # il thread conosce l'indirizzo del client e la connessione perchè si usa
        # una zona di memoria condivisa
        Thread(target=connection_manager_thread, args=(addr, conn), ).start()

        # qui sto generando il thread della funzione
        # connection_manager_thread e gli sto passando come argomenti addr e conn, cioè i parametri della connessione
        # appena stabilita. Il thread principale quindi crea questo thread che gestisce la connessione e torna subito
        # a mettersi in ascolto di nuove connessioni

        # in questo caso non ci sono misure di sicurezza che gestiscono la creazione di thread, però eventualemte in una
        # architettura vera distribuita ci potrebbero essere una serie di controllori di qualità della richiesta.
        # (ad esempio potrebbero arrivare 10000 richieste dallo stesso IP ed è un rischio).

    TCPServerSocket.close()