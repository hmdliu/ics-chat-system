# -*- coding: utf-8 -*-
"""
Created on Sat Dec 8 08:41:19 2019

@author: hl3797
"""

import os
import sys
import json
import pickle
import threading
from shutil import copy
from Cloud_zip import *
from chat_utils import *
from Ftp_client_class import *
from CloudIndex_class import *

class Cloud:
    def __init__(self, sock, name):
        self.sock = sock
        self.name = name
        self.file_idx = {}
        self.key = self.get_key()
        self.ftp_client = MyFtp()
        self.get_file_index()
        # self.cloud_cmdl()

    def get_key(self):
        key_f = open('key', 'rb')
        key_dic = pickle.load(key_f)
        key_f.close()
        return key_dic[self.name].decode()

    def request(self, jsn):
        mysend(self.sock, jsn, self.name)
        server_msg = json.loads(myrecv(self.sock, 'client', self.name))
        return server_msg

    def get_file_index(self):
        try:
            cmd_msg = json.dumps({"action": "cloud", "cmd": "get_file_index"})
            self.file_idx = self.request(cmd_msg)['index']
            # print(self.file_idx, '\n')
        except Exception as err:
            self.file_idx = {0:'error'}
            print(err, '\n')

    def format_str(self, s, length, p, ch):
        if len(s) < length:
            if p == 0:
                return s + ch * (length - len(s))
            else:
                return ch * (length - len(s)) + s
        else:
            return s

    def cloud_ls(self):
        file_list = '' # ' Index  File_name'
        print('\n[File List]:\n')
        for idx in self.file_idx.keys():
            if idx != '-1':
                file_list += '    ' + self.format_str(str(idx), 3, 1, '0') + '   '  \
                    + self.format_str(self.file_idx[idx]['name'], 19, 0, ' ') \
                    + 'Time:' + self.file_idx[idx]['time'] + '\n'
        print(file_list, '\n')

    def get_file_info(self, file_idx):
        file_info = ''
        target = self.format_str(file_idx, 3, 1, '0')
        for idx in self.file_idx.keys():
            current = self.format_str(idx, 3, 1, '0')
            if target == current:
                file_info += '     Idx: ' + current + '\n'
                file_info += '    Name: ' + self.file_idx[idx]['name'] + '\n'
                file_info += '    Time: ' + self.file_idx[idx]['time'] + '\n'
                file_info += '    Size: ' + self.file_idx[idx]['size'] + '\n'
                file_info += '    Ownr: ' + self.file_idx[idx]['owner'] + '\n'
        return '\n\n[File Info]:\n\n' + file_info

    def cloud_info(self, file_idx):
        file_info = ''
        target = self.format_str(file_idx, 3, 1, '0')
        for idx in self.file_idx.keys():
            current = self.format_str(idx, 3, 1, '0')
            if target == current:
                file_info += '     Idx: ' + current + '\n'
                file_info += '    Name: ' + self.file_idx[idx]['name'] + '\n'
                file_info += '    Time: ' + self.file_idx[idx]['time'] + '\n'
                file_info += '    Size: ' + self.file_idx[idx]['size'] + '\n'
                file_info += '    Ownr: ' + self.file_idx[idx]['owner'] + '\n'
        if file_info != '':
            print('\n[File Info]:\n\n' + file_info)
        else:
            print('\nNo such an index.\n\n')

    def cloud_delete(self, file_idx):
        cmd_msg = json.dumps({"action": "cloud", "cmd": "delete", "file_idx":file_idx})
        rsp_msg = self.request(cmd_msg)
        self.get_file_index()
        print(rsp_msg['result'], '\n')

    def cloud_recv(self, owner, file_idx):
        cmd_msg = json.dumps({"action": "cloud", "cmd": "recv", "file_idx":file_idx, "owner":owner})
        rsp_msg = self.request(cmd_msg)
        self.get_file_index()
        if rsp_msg['result'] == 1000:
            print('Received successfully.\n')
        else:
            print('Failed to receive.\n')

    def cloud_upload(self, path, filename):
        try:
            status_code = zip_compress(path, filename, self.key, False)
            if self.ftp_client.ftp_login('localhost', self.name, self.key) == 1000 and status_code == 1000:
                status_code = self.ftp_client.stor_file(filename + '.zip')
                if status_code == 1000:
                    cmd_msg = json.dumps({"action": "cloud", "cmd": "upload", "filename":filename})
                    status_code = self.request(cmd_msg)["result"]
                    # print(status_code)
                    if status_code == 1000:
                        print('Upload success.', '\n')
                        os.remove(path + filename + '.zip')
                    else:
                        print('Upload fail.', '\n')
                    self.get_file_index()
            else:
                print('[Cloud Upload] Zip Error or no such a file.\n')
        except Exception as err:
            print('[Cloud Upload]', err)

    def cloud_download(self, path, file_idx):
        # try:
            os.chdir(PROJECT_PATH)
            cmd_msg = json.dumps({"action": "cloud", "cmd": "download", "file_idx":file_idx})
            status_code = self.request(cmd_msg)["result"]
            # print(self.file_idx)
            # print(self.file_idx.keys)
            if os.path.exists(self.file_idx[str(int(file_idx))]['name']):
                print('File already exists.\n')
                os.system('start explorer ' + PROJECT_PATH)
                return
            if os.path.exists('.\\Download\\' + self.file_idx[str(int(file_idx))]['name']):
                print('File already exists.\n')
                os.system('start explorer ' + PROJECT_PATH + '.\\Download\\')
                return
            # print(type(status_code))
            if status_code == 1000:
                if self.ftp_client.ftp_login('localhost', self.name, self.key) == 1000:
                    filename = self.file_idx[str(int(file_idx))]['name']
                    status_code = self.ftp_client.retr_file(filename + '.zip')
                    if status_code == 1000:
                        status_code = zip_decompress('./', filename + '.zip', self.key, True)
                        if status_code == 1000:
                            print('Download success.', '\n')
                            os.chdir(PROJECT_PATH)
                            copy(filename, '.\\Download\\')
                            os.remove(filename)
                            os.system('start explorer ' + PROJECT_PATH + '.\\Download\\')
                        else:
                            print('Download fail. Error Code:[Unzip]', status_code, '\n')
                    else:
                        print('Download fail. Error Code:[Retr]', status_code, '\n')
                else:
                    print('Download fail. Error Code:[Login]', status_code, '\n')
            else:
                print('Download fail. Error Code:[Request]', status_code, '\n')
        # except Exception as err:
        #     print('[Cloud Download]', err)


class Cloud_init:
    def __init__(self, name):
        self.name = name
        self.path = '.\\user\\' + name + '\\cloud\\'
        self.cloud_idx = CloudIndex(name)
        self.get_key()
        self.cloud_init()

    def get_key(self):
        key_f = open('key', 'rb')
        key_dic = pickle.load(key_f)
        key_f.close()
        self.key = key_dic[self.name].decode()
        # print(self.key)

    def cloud_init(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        welcome_f = open(self.path + 'Welcome.txt', 'w')
        welcome_f.write('Welcome to ICS Cloud Disk!')
        welcome_f.close()
        status_code = zip_compress(self.path, 'Welcome.txt', self.key, True)
        if status_code == 1000:
            self.cloud_idx.add_file('Welcome.txt', self.name)
        else:
            print('[Cloud Init] Welcome.txt Error\n')

if __name__ == "__main__":

    # Initialize Cloud class
    c = Cloud_init('a')
    print('\n', c.cloud_idx.get_file_index())

    # c = Cloud('', 'xg7')
