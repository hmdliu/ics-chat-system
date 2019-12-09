# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:28:36 2019

@author: Chen Xilin, hl3797
"""

import os
import time
import pickle
from Cloud_zip import *
from chat_utils import PROJECT_PATH

class CloudIndex:
    def __init__(self, username):
        self.name = username
        self.path = '.\\user\\' + username + '\\cloud\\'
        self.key = self.get_key(username)
        # Expected outcome: self.file_index = {filename_1: owner_1, filename_2: owner_2, ... }
        self.file_index = {}
        self.index_count = 0
        self.init_file_idx()

    def get_ctime(self):
        return time.strftime('[%y.%m.%d] %H:%M', time.localtime())

    def format_size(self, b_size):
        try:
            b_size = float(b_size)
            k_size = b_size / 1024
        except Exception as err:
            print('[Format File Size]', err, '\n')
        if k_size >= 1024:
            m_size = k_size / 1024
            return '{:.2f}Mb'.format(m_size)
        else:
            return '{:.2f}Kb'.format(k_size)

    def get_file_size(self, path):
        try:
            size = os.path.getsize(path)
            return self.format_size(size)
        except Exception as err:
            print('[Get File Size]', err, '\n')

    def init_file_idx(self):
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
                idx_f = open(self.path + 'file.idx', 'wb')
                idx_f.close()
                self.file_index[-1] = {'name':'file.idx', 'owner':self.name, 'time':self.get_ctime(), 'size':'1Kb'}
                self.dump_index()
            print('[' + self.name + '] Initialize cloud file index.')
        except Exception as err:
            print('[Init index]', err, '\n')

    def dump_index(self):
        try:
            idx_f = open(self.path + 'file.idx', 'wb')
            pickle.dump(self, idx_f)
            idx_f.close()
            print('[' + self.name + '] Dump file index.')
        except Exception as err:
            print('[Dump Index]', err, '\n')

    def get_file_index(self):
        print('[' + self.name + '] Request for file index.')
        return self.file_index

    def get_key(self, name):
        try:
            # the position of the file that stores the key: './user/' + self.name + '/key'
            key_f = open('./user/' + name + '/key', 'rb')
            # load the file as a dictionary
            return pickle.load(key_f)['key'].decode()
        except Exception as err:
            print('[Get Key]', err, '\n')

    def get_filename(self, username, file_idx):
        try:
            path = '.\\user\\' + username + '\\cloud\\'
            file_idx_f = open(path + 'file.idx', 'rb')
            file_idx_dic = pickle.load(file_idx_f).file_index
            if int(file_idx) in file_idx_dic.keys():
                return (1000, file_idx_dic[int(file_idx)]['name'])
            else:
                return (1001, 'No such an index.')
        except Exception as err:
            print('[Get Filename]', err)
            return (1002, err)

    def name_to_index(self, username, filename):
        try:
            path = '.\\user\\' + username + '\\cloud\\'
            file_idx_f = open(path + 'file.idx', 'rb')
            file_idx_dic = pickle.load(file_idx_f).file_index
            file_idx_f.close()
            for idx in file_idx_dic.keys():
                if file_idx_dic[idx]['name'] == filename:
                    idx_ = '000' if len(str(idx)) > 3 else '0' * (3 - len(str(idx))) + str(idx)
                    return idx_
            return '000'
        except Exception as err:
            print('[Name -> Idx ]', err)

    def track_owner(self, file_idx, owner, filename):
        try:
            path = '.\\user\\' + owner + '\\cloud\\'
            file_idx_f = open(path + 'file.idx', 'rb')
            file_idx_dic = pickle.load(file_idx_f).file_index
            file_idx_f.close()
            idx = int(file_idx)
            if file_idx_dic[idx]['name'] == filename:
                if file_idx_dic[idx]['owner'] != owner:
                    owner_ = file_idx_dic[idx]['owner']
                    idx_ = self.name_to_index(owner_, filename)
                    return self.track_owner(idx_, owner_, filename)
                else:
                    idx_ = '000' if len(str(idx)) > 3 else '0' * (3 - len(str(idx))) + str(idx)
                    return (1000, idx_, owner)
            else:
                # print(file_idx_dic)
                # print(file_idx, owner, filename)
                return (1001, '000', 'No such a file.')
        except Exception as err:
            print('[Get Filename]', err)
            return (1002, '000', err)

    def recv_file(self, file_idx, from_name, owner):
        flag = True
        os.chdir(PROJECT_PATH)
        tp = self.get_filename(owner, file_idx)
        if tp[0] == 1000:
            filename = tp[1]
            # print(filename)
        else:
            raise Exception('[Recv File] Filename Error')
        status_code, file_idx, owner = self.track_owner(file_idx, owner, filename)
        # print(status_code, file_idx, owner)
        if status_code == 1000:
            path = '.\\user\\' + owner + '\\cloud\\'
            # filename = self.get_filename(owner, file_idx)
            if not os.path.exists(path + filename + '.zip'):
                flag = False
                print('[' + self.name + '] Requested to receive file [' + filename + ']. File not found.')
                return 1001
            if flag:
                self.file_index[self.index_count] = {'name':filename, 'owner':owner, 'time':self.get_ctime(), 'size':self.get_file_size(path + filename + '.zip')}
                self.index_count += 1
                print('[' + self.name + '] Received file [' + filename + ']')
                self.dump_index()
                return 1000
        else:
            print('[Track User Error] Code:' + str(status_code))

    def add_file(self, filename, owner):
        flag = True
        # filename += '.zip'
        os.chdir(PROJECT_PATH)
        if owner == self.name:
            if not os.path.exists(self.path + filename + '.zip'):
                flag = False
                print('[' + self.name + '] Requested to add file [' + filename + ']. File not found.')
                return 1001
        if flag:
            self.file_index[self.index_count] = {'name':filename, 'owner':owner, 'time':self.get_ctime(), 'size':self.get_file_size(self.path + filename + '.zip')}
            self.index_count += 1
            print('[' + self.name + '] Added file [' + filename + ']')
            self.dump_index()
            return 1000

    def delete_file(self, file_idx):
        try:
            idx = int(file_idx)
            if idx in self.file_index.keys():
                filename = self.file_index[idx]['name']
                if os.path.exists(self.path + filename + '.zip'):
                    os.remove(self.path + filename + '.zip')
                idxs = list(self.file_index.keys())
                for i in idxs:
                    if self.file_index[i]['name'] == filename:
                        del self.file_index[i]
                print('[' + self.name + '] Deleted file [' + filename + ']')
                self.dump_index()
                return 'The file has been deleted successfully.'
            else:
                return 'No such a file. Please check the index.'
        except Exception as err:
            print('[Delete File]', err, '\n')
            return 'Server error.'


    def fetch_file(self, file_idx, from_name):

        try:
            idx = int(file_idx)
            # print('Fetch', file_idx, from_name)
            if idx in self.file_index.keys():
                file_name = self.file_index[idx]['name']
                file_owner = self.file_index[idx]['owner']
                # print(file_name, file_owner)
                if from_name == file_owner:
                    return 1000
                elif os.path.exists(self.path + file_name + '.zip'):
                    return 1000
                else:
                    try:
                        os.chdir(PROJECT_PATH)
                        owner_path = './user/' + file_owner + '/cloud/'
                        new_path = './user/' + from_name + '/cloud/'
                        ori_key = self.get_key(file_owner)
                        new_key = self.key
                        print(ori_key, new_key)
                        # print(owner_path + file_name + '.zip')
                        if os.path.exists(owner_path + file_name + '.zip'):
                            status_code = zip_recrypt(owner_path, new_path, file_name + '.zip', ori_key, new_key)
                            return status_code
                        else:
                            return 1001
                    except Exception as err:
                        print('[Zip Recryption]', err, '\n')
                        return 1002

            else:
                return 1003
        except Exception as err:
            print('[Download File]', err)
            return 1004

if __name__ == "__main__":

    test_user = 'a'
    path  = './user/' + test_user + '/cloud/file.idx'
    c = pickle.load(open(path, 'rb'))
    print(c.get_file_index(), '\n')

    # print(c.recv_file('001', 'a', 'b'))
