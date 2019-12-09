# -*- coding: utf-8 -*-
"""
Created on Sat Dec 9 13:14:19 2019

@author: hl3797
"""

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import pickle
import os

def main():
    ftp_authorizer = DummyAuthorizer()
    key_f = open('key', 'rb')
    key_dic = pickle.load(key_f)
    key_f.close()
    for username in key_dic.keys():
        # print(username, key_dic[username].decode())
        if os.path.exists('./user/' + username + '/cloud/'):
            ftp_authorizer.add_user(username, key_dic[username].decode(), './user/' + username + '/cloud/', perm='lrdw')
    ftp_handler = FTPHandler
    ftp_handler.authorizer = ftp_authorizer
    ftp_handler.passive_ports = range(12000, 12333)
    ftp_server = FTPServer(('localhost', 2121), ftp_handler)
    ftp_server.serve_forever()

main()
