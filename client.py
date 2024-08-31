import sys
import time
import socket
import threading
import os
import shutil

class client(object):
    def __init__(self, args):
        self.server_ip = args[1] 
        self.server_port = int(args[2])
        self.client_port = int(args[3])
        self.logined = False
        self.username = ''

        self.UDPlistener = None
        self.UDPsender = None
        self.TCPlistener = None
        self.alive = True
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.server_ip, self.server_port))
        
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsocket.bind(("127.0.0.1",self.client_port))
        
        self.udp_task = []
        self.rec_filename = ''
        
        self.login()
        return
            
    def login(self):
        username = input('Username:')
        while not self.logined and self.alive:
            password = input('Password:')
            
            # LOG username password
            self.clientSocket.send(("LOG {} {}".format(username, password)).encode())
            
            reply = ''
            while reply == '':
                reply = str(self.clientSocket.recv(1024).decode('utf8'))
                
            if reply == "Login Success":
                print('Welcome to Toom!')
                self.username = username
                self.logined = True
                return
            elif reply == "Password Error":
                print("Invalid Password. Please try again")
            elif reply == "Too many failed attempts":
                print("Invalid Password. Your account has been blocked. Please try again later")
                return
            elif reply == "Blocked":
                print("Your account is blocked due to multiple login failures. Please try again later")
                return
            elif reply == "Error Username":
                username = input('Error Username! Username:')
    
    
    def UDPlisten(self):
        while self.alive:
            if self.rec_filename != "":
                with open(self.rec_filename, 'wb+') as f:
                    while True:
                        data, _ = self.udpsocket.recvfrom(4096)
                        if str(data) != "b'end'":
                            f.write(data)
                        else:
                            break
                    self.rec_filename = ""
            
            time.sleep(0.2)
                
        
    def UDPsend(self):
        while self.alive:
            if len(self.udp_task) > 0:
                # task = [UDP, IP, PORT, FILENAME]
                task = self.udp_task.pop().split(' ')
                ip = task[1]
                port = task[2]
                filename = task[3]
                
                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(4096)
                        if str(data) != "b''":
                            self.udpsocket.sendto(data,(ip, int(port)))
                        else:
                            self.udpsocket.sendto('end'.encode('utf-8'),(ip, int(port)))
                            break
                print("{} has uploaded".format(task[3]))
                
            time.sleep(0.2)
    
    
    def TCPlisten(self):
        while self.alive:
            reply = str(self.clientSocket.recv(1024).decode('utf8'))
            if reply[:3] == "UDP":
                time.sleep(0.2)
                self.udp_task.append(reply)
            elif reply[:3] == "REC":
                self.rec_filename = reply.split(" ")[-1]
            else:
                print(reply)
            time.sleep(0.2)

    
    def start(self):
        self.clientSocket.send(("UDPPORT {} {}".format(self.username, self.client_port)).encode())
        self.UDPlistener = threading.Thread(target=self.UDPlisten)
        self.UDPlistener.start()
        self.UDPsender = threading.Thread(target=self.UDPsend)
        self.UDPsender.start()
        
        # v_name = threading.Thread(method, args)
        self.TCPlistener = threading.Thread(target=self.TCPlisten)
        self.TCPlistener.start()
        
        while self.alive:
            msg = input('Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT):')
            # BCM 123 2
            self.clientSocket.send((msg + " " + self.username).encode())
            time.sleep(0.1)
            if msg == "OUT":
                self.alive = False
                print("Bye, {}!".format(self.username))
                time.sleep(0.1)
                os._exit(0)
    
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Input Error!")
    else:
        c = client(sys.argv)
        if c.logined:
            c.start()
        #Server.listen()
    