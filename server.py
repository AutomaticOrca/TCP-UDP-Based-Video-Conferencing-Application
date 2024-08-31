import sys
import time
import socket
import os
import shutil
import random
import threading
from datetime import datetime


class Server(object):
    def __init__(self, args):
        self.alive = True
        self.port = int(args[1])
        self.number_of_consecutive_failed_attempts = int(args[2])
        
        self.users = {}
        self.build_from_credentials()
        self.online_users = {}  # username: {"TCPsocket": ... , "Logintime": ... , "Ip": ... , "Port": ... , "Room" : }
        self.block_users = {}   
        self.chat_rooms = {}
        
        self.max_room = 1000
        
        try:
            with open("./messagelog.txt", 'r') as f:
                self.msgnum = len(f.readlines())
        except:
            self.msgnum = 0
        
    
    def build_from_credentials(self):
        with open("./credentials.txt", "r") as f:
            lines = f.readlines()
        for l in lines:
            # hans falcon*solo
            self.users[l.split(" ")[0]] = l.split(" ")[1].strip()
            
        
    def start(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('127.0.0.1', self.port))
        serverSocket.listen(2)
        print("Server started! Port number: {}, number of attempts: {}".format(self.port, self.number_of_consecutive_failed_attempts))

        while self.alive:
            try:
                client_socket, client_addr = serverSocket.accept()
                Server_thread = threading.Thread(target=self.reactor, args=(client_socket, client_addr))
                Server_thread.start()

            except:
                continue
            
    
    def reactor(self, client_socket, client_addr):
        attemp_times = 0
        client_ip = client_addr[0]
        client_port = client_addr[1]
        
        while self.alive:
            try:
                # msg: receive clients' message
                msg = str(client_socket.recv(1024).decode('utf8'))
            except ConnectionAbortedError:
                return 0
            except ConnectionResetError:
                return 0
            if msg == '':
                continue
            
            # client's message: 
            msg = msg.split(" ")
            reply = ""
            
            # LOG username password
            # ['LOG', username, password]
            if msg[0] == 'LOG':
                if msg[1] in list(self.block_users.keys()): # this is a blocked user
                    if time.time() - self.block_users[msg[1]] < 10: # in 10 seconds
                        client_socket.send(("Blocked").encode())    
                        return
                if msg[1] in list(self.users.keys()):   
                    if msg[2] == self.users[msg[1]]:    # match password
                        reply = "Login Success"     
                        # username: {"TCPsocket": ... , "Logintime": ... , "Ip": ... , "Port": ... , "Room" : }
                        self.online_users[msg[1]] = {}
                        self.online_users[msg[1]]["TCPsocket"] = client_socket
                        self.online_users[msg[1]]["Logintime"] = datetime.fromtimestamp(time.time()).strftime("%d %b %Y %H:%M:%S")
                        self.online_users[msg[1]]["Ip"] = client_ip
                        self.online_users[msg[1]]["Port"] = client_port
                        self.online_users[msg[1]]["Room"] = []
                    else:
                        reply = "Password Error"    # not match password
                        attemp_times += 1
                        print("{} : {}".format(msg[1], attemp_times))
                        
                    if attemp_times >= self.number_of_consecutive_failed_attempts:  # input too fast, block him/her
                        client_socket.send(("Too many failed attempts").encode())
                        self.block_users[msg[1]] = time.time()
                        return
                else:
                    reply = "Error Username"
            elif msg[0] == 'UDPPORT':
                self.online_users[msg[1]]["UDPPORT"] = msg[2]
            # [BCM, text, clientname]
            elif msg[0] == 'BCM':   
                self.msgnum += 1
                timestamp = datetime.fromtimestamp(time.time()).strftime("%d %b %Y %H:%M:%S")
                usr = msg[-1]
                with open("./messagelog.txt", 'a+') as f:
                    # "{}; {}; {}; {}\n"
                    f.write("{}; {}; {}; {}\n".format(self.msgnum, timestamp, usr, msg[1]))
                
                reply = "Broadcast message, #{} broadcast at {}.".format(self.msgnum, timestamp)    # client terminal
                bcmsg = '{} broadcasted BCM #{} "{}" at {}.'.format(usr, self.msgnum, msg[1], timestamp)    # server terminal
                # for k,v in self.online_users.items():
                #     if usr != k:
                #         v["TCPsocket"].send((bcmsg).encode())
                print(bcmsg)
            elif msg[0] == 'ATU':
                reply = ''
                usr = msg[-1]
                timestamp = datetime.fromtimestamp(time.time()).strftime("%d %b %Y %H:%M:%S")
                # self.online_users = {username:{}, ....}
                for k,v in self.online_users.items():
                    if usr != k:
                        reply += "{}, {}, {}, active since {}\n".format(k, v["Ip"], v["Port"], v["Logintime"])
                print("{} issued ATU command".format(usr))
                print("Return messages:")
                print(reply)
                
            # [SRB, usr1.... , hostuser]
            elif msg[0] == 'SRB':
                if len(msg) < 3:
                    reply = "Not enough users for char room."
                else:
                    reply = ''
                    check_available = True
                    host_usr = msg[-1]
                    all_usr = msg[1:-1]
                    all_usr.append(host_usr)
                    all_usr.sort()
                    
                    for u in all_usr:
                        if u == host_usr:
                            continue
                        else:
                            if u not in self.users.keys():
                                check_available = False
                                reply += "{} not exist!\n".format(u)
                                continue
                            if u not in self.online_users.keys():
                                check_available = False
                                reply += "{} not online!\n".format(u)
                                continue
                    
                    # [1,2,3]
                    # self.chat_rooms = {"1,2,3" : 505}
                    if check_available and ",".join(all_usr) in self.chat_rooms.keys():
                        check_available = False
                        reply += "a separate room (ID: {}) already created for these users".format(self.chat_rooms[",".join(all_usr)])
                    
                    # self.chat_rooms = {"1,2,3" : 505; 505 : [1,2,3]}
                    if check_available:
                        cur_room = str(random.randint(0, self.max_room))
                        self.chat_rooms[",".join(all_usr)] = cur_room
                        self.chat_rooms[cur_room] = []
                        for u in all_usr:
                            self.chat_rooms[cur_room].append(u)
                            self.online_users[u]["Room"].append(cur_room)
                            
                            
                        reply = 'Separate chat room has been created, room ID: {}, users in this room:'.format(cur_room)
                        reply += ",".join(self.chat_rooms[cur_room])
                        print("{} issued SRB command".format(msg[-1]))
                        print("Return messages:")
                        print(reply)
                        
            elif msg[0] == 'SRM' and len(msg) > 2:
                usr = msg[-1]
                room_id = msg[1]
                # Check whether roomID existed 
                if room_id not in self.chat_rooms.keys():
                    reply = "The separate room does not exist!"
                # Check requesting user exist in this room
                elif room_id not in self.online_users[usr]["Room"]:
                    reply = "You are not in this separate room chat!"
                else:
                    text = msg[2]
                    try:
                        with open("./SR_{}_messageLog.txt".format(room_id), "a+") as f:
                            _ = f.readlines()
                        room_msg_num = len(_) + 1   # get number of message is this room
                    except:
                        room_msg_num = 1
                    timestamp = datetime.fromtimestamp(time.time()).strftime("%d %b %Y %H:%M:%S")
                    text = "{}; {}; {}; {}".format(room_msg_num, timestamp, usr, msg[2])
                    # put message text in this txt file
                    with open("./SR_{}_messageLog.txt".format(room_id), "a+") as f:
                        f.write(text + '\n')
                        
                    print("{} issued a message in separate room {}:".format(usr, room_id))
                    print(text)
            elif msg[0] == 'RDM' and (msg[1] == 's' or msg[1] == 'b'):
                type = msg[1]
                usr = msg[-1]
                reply = ""
                t = datetime.strptime(" ".join(msg[2:-1]), "%d %b %Y %H:%M:%S")
                if type == 'b':
                    with open("./messagelog.txt", 'r') as f:
                        lines = f.readlines()
                    for l in lines:
                        #l = "2; 30 Jul 2022 11:26:08; 2; 123"
                        ts = datetime.strptime(l.split(";")[1], " %d %b %Y %H:%M:%S")
                        if ts > t:
                            reply += l
                else:
                    for room_id in self.online_users[usr]["Room"]:
                        with open("./SR_{}_messageLog.txt".format(room_id), 'r') as f:
                            lines = f.readlines()
                            for l in lines:
                                ts = datetime.strptime(l.split(";")[1], " %d %b %Y %H:%M:%S")
                                if ts > t:
                                    reply += l
                print("RDM command issued from {}".format(usr))
                print("Return messages:")
                print(reply)
     
            elif msg[0] == 'OUT':
                usr = msg[-1]
                del self.online_users[usr]
                print("{} logout".format(usr))
            elif msg[0] == 'UPD':
                usr = msg[-1]
                target = msg[1]
                filename = msg[2]
                if target in self.online_users.keys():
                    reply = "UDP {} {} {}".format(self.online_users[target]["Ip"], self.online_users[target]["UDPPORT"], filename)
                    self.online_users[target]["TCPsocket"].send(("Received {} from {}".format(filename, usr)).encode())
                    time.sleep(0.1)
                    self.online_users[target]["TCPsocket"].send(("REC {}".format(filename)).encode())
                else:
                    reply = "{} not online!".format(target)
            else:
                reply = "Error. Invalid command!"
            client_socket.send((reply).encode())
            
            
            

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Input Error!")
    else:
        Server = Server(sys.argv)
        Server.start()