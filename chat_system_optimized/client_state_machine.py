"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang, hl3797
"""
from chat_utils import *
from Cloud_disk_cmdl import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name
        self.cloud = Cloud(self.s, self.me)

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg, self.me)
        response = json.loads(myrecv(self.s, 'client', self.me))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg, self.me)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    mysend(self.s, json.dumps({"action":"logout"}), self.me)
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}), self.me)
                    time_in = json.loads(myrecv(self.s, 'client', self.me))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}), self.me)
                    logged_in = json.loads(myrecv(self.s, 'client', self.me))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:].strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}), self.me)
                    search_rslt = json.loads(myrecv(self.s, 'client', self.me))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].strip().isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}), self.me)
                    poem = json.loads(myrecv(self.s, 'client', self.me))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg == 'ping blah blah':
                    mysend(self.s, json.dumps({"action":"bonus"}), self.me)
                    server_msg = json.loads(myrecv(self.s, 'client', self.me))["message"]
                    self.out_msg += server_msg

                elif my_msg[:7] == '_cloud_':
                    cmd = my_msg.split(' ')
                    if len(cmd) > 1:
                        # c = Cloud(self.s, self.me)
                        if cmd[1] == 'ls':
                            self.cloud.cloud_ls()
                        elif cmd[1] == 'info':
                            try:
                                self.cloud.cloud_info(cmd[2])
                            except Exception as err:
                                print('Please add file index.\n')
                        elif cmd[1] == 'del':
                            try:
                                self.cloud.cloud_delete(cmd[2])
                            except Exception as err:
                                print(err)
                                print('Please add file index.\n')
                        elif cmd[1] == 'upload':
                            try:
                                if '.' in cmd[2]:
                                    self.cloud.cloud_upload('./', cmd[2])
                                else:
                                    print('Invalid file type.\n')
                            except Exception as err:
                                print(err)
                                print('Please add filename.\n')
                        elif cmd[1] == 'download':
                            # try:
                                self.cloud.cloud_download('./', cmd[2])
                            # except Exception as err:
                            #     print(err)
                            #     print('Please add file index.\n')
                        else:
                            print('Invalid command.\n')


                    else:
                        print('Invalid command.\n')

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg

                if peer_msg["action"] == "connect":

                    # ----------your code here------#
                    # print(peer_msg)
                    self.peer = peer_msg['from']
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You have been connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    # ----------end of your code----#

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                if my_msg[:6] == '_flip_':
                    exchage_msg = '_flip_ ' + ' '.join(my_msg[6:].strip().split(' ')[::-1])
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":exchage_msg}), self.me)
                elif my_msg[:7] == '_cloud_':
                    cmd = my_msg.split(' ')
                    if cmd[1] == 'ls' and len(cmd) == 2:
                        self.cloud.cloud_ls()
                    elif cmd[1] == 'share' and len(cmd) == 3 and len(cmd[2]) == 3:
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg + self.cloud.get_file_info(cmd[2])}), self.me)
                    elif cmd[1] == 'recv' and len(cmd) == 4 and len(cmd[3]) == 3:
                        self.cloud.cloud_recv(cmd[2], cmd[3])
                    elif cmd[1] == 'info' and len(cmd) == 3 and len(cmd[2]) == 3:
                        self.cloud.cloud_info(cmd[2])
                    else:
                        print(CHAT_CLOUD_CMD)
                else:
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}), self.me)
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''

            if len(peer_msg) > 0:    # peer's stuff, coming in


                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                # print(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg['from'] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    # self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    self.out_msg += peer_msg['message']
                else:
                    self.out_msg += peer_msg['message']
                # ----------end of your code----#

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
