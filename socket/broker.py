import socket
from sys import argv
import re
from threading import Thread, Lock
import json


def decodeCommand(message, stato):
    # NBB da mandare con doppi apici senza caratteri speciali
    # due regular expression, all'interno di '[]' deve venir mandato un messaggio e la rende disponibile come parametro
    regexCOMMAND = r"^\[([A-Z]+)\]"
    # in questo caso qui riconosce la serializzazione come stringa di un file json
    # cioè aperte e chiude parantesi graffe con più coppie chiave valore al suo interno.
    regexJSON = r"(\{[\"a-zA-Z0-9\,\ \:\"\]\[]+\})"

    withArgs = {"SUBSCRIBE", "UNSUBSCRIBE", "SEND"}

    # qui vado a cercare l'eventuale comando e lo metto nella variabile command
    command = re.findall(regexCOMMAND, message)[0]
    comando = None

    if command:
        comando = dict()
        comando['azione'] = command  # comando diventa un dizionario dove la chiave è azione e il value è il comando
        # ricevuto dal client
        if command in withArgs and stato == "CONNESSO":
            stringa = re.findall(regexJSON, message)[0]
            parametri = json.loads(stringa)  # il json conterrà il parametro dell'azione ad esempio SUBSCRIBE '2' dove 2
            # identifica il topic al quale voglio iscrivermi
            comando['parametri'] = parametri

    return comando


def updateState(id_, stato, comando):
    global activeConnections
    global mutexACs

    if stato == "PRE-CONNESSIONE":  # in preconnessione sono collegato a livello TCP ma non sono ancora abilitato a fare
        # richieste di sottoscrizioni ed invio di messaggi
        if comando['azione'] == "CONNECT":
            newStato = "CONNESSO"  # questo è il livello di connessione applicativo (quello TCP sta effettivamente quando
            # accetto la connessione
            mutexACs.acquire()
            activeConnections[id_]['connected'] = True
            mutexACs.release()
            print('{} connected!'.format(id_))

            return newStato

    if stato == "CONNESSO":
        if comando['azione'] == "DISCONNECT":
            newStato = "IN-USCITA"
            return newStato

    return stato


def subscribe(id_, conn, comando):
    global activeConnections
    global mutexACs
    global mutexTOPICs
    global topics

    if "topic" in comando['parametri']:

        topic = comando['parametri']['topic']

        mutexACs.acquire()
        activeConnections[id_]["topics"].add(topic)
        mutexACs.release()

        mutexTOPICs.acquire()
        if not topic in topics:
            topics[topic] = set()
        topics[topic].add(id_)
        mutexTOPICs.release()
        print(topics)

        response = 'Sottoscritto al topic: {}\n'.format(topic)
        conn.sendall(response.encode())


def unsubscribe(id_, conn, comando):
    global activeConnections
    global mutexACs
    global mutexTOPICs
    global topics

    topic = comando['parametri']['topic']

    mutexACs.acquire()
    activeConnections[id_]["topics"].remove(topic)
    mutexACs.release()

    mutexTOPICs.acquire()
    if topic in topics:
        if id_ in topics[topic]:
            topics[topic].remove(id_)
        if len(topics[topic]) == 0:
            del topics[topic]
    mutexTOPICs.release()
    print(topics)

    response = 'Cancellazione della sottoscrizione al topic: {}\n'.format(topic)
    conn.sendall(response.encode())


def send(id_, conn, comando):
    global activeConnections
    global mutexACs
    global mutexTOPICs
    global topics

    topic = comando["parametri"]["topic"]
    message = comando["parametri"]["message"]

    risposta = dict()
    risposta["id"] = id_
    risposta["topic"] = topic
    risposta["messaggio"] = message
    # serializzo il dizionario facendolo diventare una stringa con un 'a capo'
    stringa = json.dumps(risposta) + '\n'
    print(stringa)

    # serve un doppio mutex perchè accedo contemporaneamente ad active connections e topics.
    mutexACs.acquire()
    mutexTOPICs.acquire()
    subscribers = topics[topic]  # insieme di tutti gli utenti registrati a quel topic
    for subID in subscribers:  # subID sarebbe ID del subscriber al topic
        recv_conn = activeConnections[subID][
            "connessione"]  # activeConnections[subID] ho il topic a cui corrisponde un ID
        recv_conn.sendall(stringa.encode())
    mutexTOPICs.release()
    mutexACs.release()


def disconnect(id_):
    global activeConnections
    global mutexACs
    global mutexTOPICs
    global topics

    mutexACs.acquire()
    curr_topics = activeConnections[id_]["topics"]
    mutexACs.release()

    mutexTOPICs.acquire()
    for topic in curr_topics:
        topics[topic].remove(id_)
        if len(topics[topic]) == 0:
            del topics[topic]  # se è l'unico utente registrato ad un topic allora rimuovo il topic
    mutexTOPICs.release()

    mutexACs.acquire()
    del activeConnections[id_]
    mutexACs.release()
    conn.close()


def applyCommand(id_, conn, comando, stato):
    if (stato == "CONNESSO"):
        if comando['azione'] == "SUBSCRIBE":
            subscribe(id_, conn, comando)
            return True
        if comando['azione'] == "UNSUBSCRIBE":
            unsubscribe(id_, conn, comando)
            return True
        if comando['azione'] == "SEND":
            send(id_, conn, comando)
            return True
        if comando['azione'] == "DISCONNECT":
            disconnect(id_)
            return True
    return False


def connection_manager_thread(id_, conn):
    stato = "PRE-CONNESSIONE"  # CONNESSO, IN-USCITA
    print('Client: {}'.format(id_))

    while not (stato == "IN-USCITA"):
        data = conn.recv(1024)
        if not data:
            break
        comando = decodeCommand(data.decode('utf-8'), stato)  # decodifica il mex inviato dal client, creando un oggetto
        # di natura comando
        applyCommand(id_, conn, comando, stato)  # applica il comando
        stato = updateState(id_, stato, comando)  # aggiorna lo stato


if __name__ == '__main__':

    localIP = argv[1]
    localPORT = int(argv[2])

    global activeConnections
    activeConnections = {}  # uguali al chat server
    global mutexACs  # serve per garantire che l'aggiornamento sul dizionario delle active connections sia fatto da un
    # thread alla volta
    global mutexTOPICs  # struttura dati che contiene i topic e i messaggi dentro i topic
    # si deve evitare che vada in conflitto con i thread che vogliono aggiornare i topic
    mutexACs = Lock()
    mutexTOPICs = Lock()
    global topics
    topics = dict()
    curr_id = -1;

    # come al solito definisco il socket aprendo la connessione
    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPORT))

    try:

        while True:
            # accetto le connessioni
            print('Broker UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
            TCPServerSocket.listen()
            conn, addr = TCPServerSocket.accept()

            mutexACs.acquire()
            # e le inserisco dentro le active connections
            activeConnections[curr_id + 1] = {
                'address': addr,
                'connessione': conn,
                'connected': False,  # è una sorta di connessione a livello applicativo, perchè a livello di
                # trasporto già ho stabilito la connessione
                'id': curr_id + 1,
                'topics': set()  # all'inizio il client non ha espresso preferenze su alcun topic in particolare
            }
            curr_id += 1

            mutexACs.release()
            # qui viene avviato il connection manager thread
            Thread(target=connection_manager_thread, args=(curr_id, conn), ).start()  #
    finally:
        if TCPServerSocket:
            TCPServerSocket.close()
