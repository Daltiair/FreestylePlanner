import sys
import socket
import threading
import datetime
import pandas as pd
from queue import Queue

NUMBER_OF_THREADS = 20  # Worker Threads to handel client connections
queue = Queue()
all_connect = []
all_addre = []
all_connect_dt = []
MAC_ADDRE = []
# Define base column lengths
baseSingleCols = 8
baseCoupleCols = 10

def create_sockets():
    try:
        global host
        global port
        global threads
        global s
        global condition
        # set up socket and connection
        host = socket.gethostbyname(socket.gethostname())
        port = 8989
        threads = []

        macadddrefile = ""
        with open(macadddrefile) as f:
            MAC_ADDRE = f.read().splitlines()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_socket(s, host, port)
        # Create worker threads
        condition = threading.Condition()
        for i in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=threadWork, args=(condition,))
            t.daemon = True
            threads.append(t)
            threads[i].start()
        # Thread for shell
        lock = threading.Lock()
        t = threading.Thread(target=power_shell, args=(lock,))
        return condition
    except:
        print("Error creating socket")


def bind_socket(s, host, port):
    try:
        print("Binding Port" + str(port))
        s.bind((host, port))
        s.listen(5)
    except:
        print("Socket Bind error \n Retrying...")


def accept_connections(condition):
    for c in all_connect:
        c.close()
    del all_connect[:]
    del all_addre[:]
    dt = datetime(1, 1, 0)
    print("Waiting for connections")
    while True:
        try:
            conn, addre = s.accept()
            s.setblocking(1)  # Stops timeout from happening
            all_connect.append(conn)
            all_addre.append(addre)
            all_connect_dt.append(dt.today())
            print("Connection to " + addre + " made")

            # Receive data from the connection
            file_name = conn.recv(1024).decode()
            mac_addr = conn.recv(1024).decode()
            if mac_addr not in MAC_ADDRE:
                conn.send("MAC Address not recognized \n Contact admin @ 5402805590")
            # fileSize = conn.recv(1024).decode()
            file_bytes = b''

            done = False
            while not done:
                data = conn.recv(1024)
                if file_bytes[-11:] == b'<Terminate>':
                    done = True
                else:
                    file_bytes += data

            with open(file_name, 'wb') as f:
                f.write(file_bytes)
                f.close()

            df_set = pd.read_excel(file_name, sheet_name='Settings', index_col=0)
            df_cat = pd.read_excel(file_name, sheet_name='Event Categories')

            # Make list of Genres
            genrelist = list(df_cat['Genre'].unique())
            # Make list of Dances/Events
            dancelist = list(df_cat['Dance'].unique())

            # Stops pandas from reading useless blank columns
            cols = []
            for i in range(len(dancelist) + baseSingleCols):
                cols.append(i)

            df_sing = pd.read_excel(file_name, sheet_name='Singles', usecols=cols)
            df_sing['id'] = ''

            # Stops pandas from reading useless blank columns
            cols = []
            for i in range(len(dancelist) + baseCoupleCols):
                cols.append(i)

            df_coup = pd.read_excel(file_name, sheet_name='Couples', usecols=cols)

            df_inst = pd.read_excel(file_name, sheet_name='Instructors')

            dfs = [df_set, df_cat, df_sing, df_coup, df_inst]

            with condition:
                # add the job to the queue
                queue.put([conn, addre, dfs])
                condition.notify()
        except:
            print("Error in connection set up")


def power_shell(lock):
    cmd = print("powershell>")

    if 'list' in cmd:
        if 'mac' in cmd:
            listMACAdd()
        else:
            with lock:
                listConnections()
    if cmd == 'prev conn':
        showPreviousConnections()
    else:
        print("Command not recongized")


def threadWork(condition):
    """Tread will continually look for work from the queue.
        If there is work, execute it
        If no work for work to be added on the queue from a condition variable in the main thread"""
    while 1:
        with condition:
            try:
                job = queue.get()
                conn = job[0]
                addre = job[1]
                dfs = job[2]
                sortData(conn, addre, dfs)
            except:
                condition.wait()


def listConnections():
    print("------------Connections--------------")
    for each in all_connect:
        print(each+'\n')

def sortData(conn, addre, dfs):
    pass

def listMACAdd():
    print("------------Registered MAC Addresses--------------")
    for each in MAC_ADDRE:
        print(each+"\n")

def showPreviousConnections():
    pass
# TODO print out the file of the last month of connections
#  connections before the 1st of this month will need to be viewed in the file system
