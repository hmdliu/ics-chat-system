"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang, hl3797
"""

import os
import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
import chat_group as grp
from chat_utils import *
from UserPwd_class import *
from Crypt_class import *
from win32api import ShellExecute

class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            # username = self.logged_sock2name[sock]
            msg = json.loads(myrecv(sock, 'server', '__OFFLINE__'))
            if len(msg) > 0:
                # print(msg)
                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:

                        path = './user/' + name + '/'

                        if msg["step"] == 'name':
                            if os.path.exists(path) and os.path.exists(path + 'key') and os.path.exists(path + name + '.pwd'):
                                name_status = 'name_ok'
                            else:
                                name_status = 'name_fail'
                            mysend(sock, json.dumps(
                                {"action": "login", "status": name_status}), '__OFFLINE__')

                        elif msg["step"] == 'pwd':
                            pwd = pkl.load(open(path + name + '.pwd', 'rb'))
                            if pwd.check_pwd(msg["pwd"]):
                                # move socket from new clients list to logged clients
                                self.new_clients.remove(sock)
                                # add into the name to sock mapping
                                self.logged_name2sock[name] = sock
                                self.logged_sock2name[sock] = name
                                # load chat history of that user
                                if name not in self.indices.keys():
                                    try:
                                        self.indices[name] = pkl.load(
                                            open('./user/' + name + '/' + name + '.idx', 'rb'))
                                    except IOError:  # chat index does not exist, then create one
                                        self.indices[name] = indexer.Index(name)
                                print('[' + name + '] logged in')
                                self.group.join(name)
                                mysend(sock, json.dumps(
                                    {"action": "login", "status": "pwd_ok"}), '__OFFLINE__')
                            else:
                                # self.new_clients.remove(sock)
                                mysend(sock, json.dumps(
                                    {"action": "login", "status": "pwd_fail"}), '__OFFLINE__')

                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}), '__OFFLINE__')
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except Exception as err:
            print(err)
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        path = './user/' + name + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        pkl.dump(self.indices[name], open(path + name + '.idx', 'wb'))
        print('[' + name + '] logged out.')
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        username = self.logged_sock2name[from_sock]
        msg = myrecv(from_sock, 'server', username)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}), g)
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg, from_name)
# ==============================================================================
# handle messeage exchange: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                from_message = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(from_message)
                # ---- end of your code --- #

                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]

                    # IMPLEMENTATION
                    # ---- start your code ---- #
                    # mysend( to_sock, "...Remember to index the messages before sending, or search won't work")
                    self.indices[g].add_msg_and_index(from_message)
                    mysend(to_sock, json.dumps({"action": "exchange", "from": from_name, "message": from_message}), g)
                    # ---- end of your code --- #

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "message": "everyone left, you are alone\n"}), g)
# ==============================================================================
#                 listing available peers: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #

                # msg = "...needs to use self.group functions to work"

                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}), from_name)
# ==============================================================================
#             retrieve a sonnet : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #

                # poem = "...needs to use self.sonnet functions to work"
                # print('here:\n', poem)

                from_name = self.logged_sock2name[from_sock]
                print('[' + from_name + '] asks for [' + msg['target'] + ']')
                try:
                    poem_idx = int(msg['target'])
                    poem = '\n'.join([str(i).strip() for i in self.sonnet.get_poem(poem_idx)])
                except Exception as err:
                    #print(err)
                    poem = 'Invalid index.'

                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}), from_name)
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                from_name = self.logged_sock2name[from_sock]
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime + '\n'}), from_name)
# ==============================================================================
#                 bonus - blah blah
# ==============================================================================
            elif msg["action"] == "bonus":
                from_name = self.logged_sock2name[from_sock]
                mysend(from_sock, json.dumps({"action": "bonus", "message": "pong blah blah\n"}), from_name)

            elif msg["action"] == "logout":
                self.logout(from_sock)

            elif msg["action"] == "cloud":
                try:
                    from_name = self.logged_sock2name[from_sock]
                    idx_path = './user/' + from_name + '/cloud/file.idx'
                    idx_f = open(idx_path, 'rb')
                    my_cloud = pkl.load(idx_f)
                    if msg["cmd"] == "get_file_index":
                        idx_data = my_cloud.get_file_index()
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "get_file_index", "index": idx_data}), from_name)
                    elif msg["cmd"] == "delete":
                        del_result = my_cloud.delete_file(msg["file_idx"])
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "delete", "result": del_result}), from_name)
                    elif msg["cmd"] == "upload":
                        add_result = my_cloud.add_file(msg["filename"], from_name)
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "upload", "result": add_result}), from_name)
                    elif msg["cmd"] == "download":
                        fetch_result = my_cloud.fetch_file(msg["file_idx"], from_name)
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "download", "result": fetch_result}), from_name)
                    elif msg["cmd"] == "recv":
                        recv_result = my_cloud.recv_file(msg["file_idx"], from_name, msg["owner"])
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "recv", "result": recv_result}), from_name)
                    else:
                        mysend(from_sock, json.dumps({"action": "cloud", "cmd": "error", "result": "error"}), from_name)


                except Exception as err:
                    print(err, '\n')
                    # mysend(from_sock, json.dumps({"action": "upload", "message": "fail\n"}))

# ==============================================================================
#                 search: : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #

                # search_rslt = "needs to use self.indices search to work"
                # print('server side search: ' + search_rslt)

                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('[' + from_name + '] search for [' + term + ']')
                search_result = '\n'.join([str(i) for i in self.indices[from_name].search(term)])

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_result}), from_name)

# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def ftp_startup(self):
        os.chdir(PROJECT_PATH)
        # os.system('dir')
        # os.system('python .\\Ftp_server.py')
        ShellExecute(0, 'open', 'python', './Ftp_server.py', '', 1)

    def run(self):
        print('starting server...')

        self.ftp_startup()

        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            # time.sleep(0.2)
            # print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            # print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('Checking for new connections & clients ...')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
