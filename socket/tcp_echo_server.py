import socket
from sys import argv
import time 

localIP     = argv[1]
localPORT   = int(argv[2])
# stiamo costruendo un servizio che si mette in attesa di comunicazione esterna tramite il protocollo TCP
# TCPServerSocket si deve specificare il tipo di socket e la famiglia di indirizzi
TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
TCPServerSocket.bind((localIP, localPORT))
# localPORT è la porta su cui il server si mette in ascolto
# localIP è l'indirizzo IP del server
# l'operazione di bind, sarebbe dove fisso l'applicazione per farla mettere in ascolto su una porta

print('TCP Server UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
TCPServerSocket.listen()  # mi metto in ascolto di nuove connessioni

# Accetto una nuova connessione
conn, addr = TCPServerSocket.accept()

print('Client: {}'.format(addr))

time.sleep(5)
while True:
    data = conn.recv(1024)

    if not data:
        break

    # print('{}: echo message: {}'.format(addr, data[:-1].decode('utf-8')))
    print('{}: echo message: {}'.format(addr, data))
    # stampo il messaggio e lo mando indietro al mittente con sendall
    conn.sendall(data)

conn.close()
# Chiudo la connessione in essere

TCPServerSocket.close()


# NB telnet usando telnet si può stabilire una connessione TCP con qualsiasi host