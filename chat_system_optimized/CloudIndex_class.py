# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:28:36 2019

@author: Chen Xilin
"""
import pickle

class CloudIndex:
    def __init__(self, username):
        self.name = username
        self.key = self.get_key()
        # Expected outcome: self.file_index = {filename_1: owner_1, filename_2: owner_2, ... }
        self.file_index = {}

    def get_key(self):
        # the position of the file that stores the key: './user/' + self.name + '/key'
        key_f = open('./user/' + self.name + '/key', 'rb')
        # load the file as a dictionary
        self.key = pickle.load(key_f)['key']

    def add_file(self, filename, owner):
        self.file_index[filename] = owner

    def del_file(self, filename):
        del self.file_index[filename]

    def fetch_file(self, filename):
        owner = self.file_index[filename]
        if owner == self.name:
            action = "D"    #"download"
        else:
            action = "R"    #"recrypt_before_download"
        return action
