import os
import time
import socket
import select
import sys
import json
import threading
from chat_utils import *
import client_state_machine as csm

class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.login_step = 'name'

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket, 'client')

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        #peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        if len(my_msg) > 0:
            # print(my_msg, self.login_step)
            if self.login_step == 'name':
                self.name = my_msg
                msg = json.dumps({"action":"login", "step":"name", "name":self.name})
            elif self.login_step == 'name_ok':
                msg = json.dumps({"action":"login", "step":"pwd", "name":self.name, "pwd":my_msg})
            self.send(msg)
            response = json.loads(self.recv())
            # print(str(response))
            if response["status"] == 'name_ok':
                self.login_step = 'name_ok'
                self.system_msg += 'Please enter the password:'
                pwd_thread = threading.Thread(target=self.read_input)
                pwd_thread.daemon = True
                pwd_thread.start()
                return (False, 'name_ok')
            elif response["status"] == 'pwd_fail':
                # self.login_step = 'pwd_fail'
                self.system_msg += 'Wrong password!\nPlease try again:'
                pwd_thread = threading.Thread(target=self.read_input)
                pwd_thread.daemon = True
                pwd_thread.start()
                return (False, 'pwd_fail')
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return (False, 'name_duplicate')
            elif response["status"] == 'pwd_ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True, 'pwd_ok')
            else:
                print('Invalid status')
        else:               # fix: dup is only one of the reasons
           return(False, 'no_msg')


    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            # print(text)
            self.console_input.append(text) # no need for lock, append is thread safe

    def print_instructions(self):
        self.system_msg += menu

    def run_chat(self):
        self.init_chat()
        self.system_msg += 'Welcome to ICS chat\n'
        self.system_msg += 'Please enter your name: '
        self.output()
        while True:
            time.sleep(0.1)
            login_msg = self.login()
            if 'pwd' in login_msg[1]:
                os.system('cls')
            if login_msg[0] == True:
                break
            self.output()
        self.system_msg += 'Welcome, ' + self.get_name() + '!'
        self.output()
        while self.sm.get_state() != S_OFFLINE:
            self.proc()
            self.output()
            time.sleep(CHAT_WAIT)
        self.quit()

#==============================================================================
# main processing loop
#==============================================================================
    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
