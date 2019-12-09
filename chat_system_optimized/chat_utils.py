import socket
import time
import os
from Crypt_class import *

# use local loop back address by default
#CHAT_IP = '127.0.0.1'
CHAT_IP = socket.gethostbyname(socket.gethostname())
#CHAT_IP = ''#socket.gethostbyname(socket.gethostname())

PROJECT_PATH = 'D:\\Github\\ics-chat-system\\chat_system_optimized'

CHAT_CLOUD_CMD = '\n\n[Cloud Commands Instructions]:\n\n  _cloud_ ls: List all your cloud files\n  _cloud_ info [idx]: View the info of a file.\n  _cloud_ share [idx]: Share a file to your friend in current group\n  _cloud_ recv [owner] [idx]: Receive a file from your friend.\n'

CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

menu = "\n++++ Choose one of the following commands\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        c [peer]: to connect to the [peer] and chat\n \
        ? [term]: to search your chat logs where [term] appears\n \
        p [#]: to get number [#] sonnet\n \
        _cloud_ ls: List all your cloud files\n \
        _cloud_ del [idx]: Delete a cloud file\n \
        _cloud_ info [idx]: View a cloud file info\n \
        _cloud_ upload [filename]: Upload a cloud file\n \
        _cloud_ download [filename]: Download a cloud file\n \
        q: to leave the chat system\n\n"

S_OFFLINE   = 0
S_CONNECTED = 1
S_LOGGEDIN  = 2
S_CHATTING  = 3

SIZE_SPEC = 5

CHAT_WAIT = 0.2

def print_state(state):
    print('**** State *****::::: ')
    if state == S_OFFLINE:
        print('Offline')
    elif state == S_CONNECTED:
        print('Connected')
    elif state == S_LOGGEDIN:
        print('Logged in')
    elif state == S_CHATTING:
        print('Chatting')
    else:
        print('Error: wrong state')

def mysend(s, msg, key):
    #append size to message and send it
    # print('send raw', msg)
    if key != '__OFFLINE__':
        ed = ED_Crypt(key)
        msg = ed.encrypt(msg).decode()
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    # print('send final', msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg) :
        sent = s.send(msg[total_sent:])
        if sent==0:
            print('server disconnected')
            break
        total_sent += sent

def myrecv(s, request_from, key):
    #receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        try:
            text = s.recv(SIZE_SPEC - len(size)).decode()
        except Exception as err:
            if request_from == 'client':
                print('The server broke down, see you next time!')
                os._exit(0)
            else:
                print(err)
            return('')
        # if not text:
        #     print('disconnected')
        #     return('')
        size += text
    size = int(size)
    #now receive message
    msg = ''
    while len(msg) < size:
        text = s.recv(size-len(msg)).decode()
        if text == b'':
            print('disconnected')
            break
        msg += text
    # print ('received '+message)
    # print('recv raw', msg)
    if key != '__OFFLINE__':
        ed = ED_Crypt(key)
        msg = ed.decrypt(msg).decode()
    # print('recv final', msg)
    return (msg)

def text_proc(text, user):
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    return('(' + ctime + ') ' + user + ' : ' + text) # message goes directly to screen
