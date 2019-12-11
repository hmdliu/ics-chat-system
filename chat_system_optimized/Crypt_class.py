# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 13:47:17 2019

@author: Chen Xilin, hl3797
"""

import os
import pickle
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class Crypt:
    def __init__(self, username, pwd):
        self.name = username
        self.pwd = pwd
        self.key = ""
        self.salt = os.urandom(16)
        self.build_key()

    def build_key(self):
        n_pwd = (self.name + self.pwd + "I_LOVE_ICS").encode()
        salt = self.salt
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,salt=salt, iterations=100000,backend=default_backend())
        self.key = base64.urlsafe_b64encode(kdf.derive(n_pwd))
        self.save_key()

    def save_key(self):

        path = './user/' + self.name + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        self_key_f = open(path + 'key', 'wb')
        self_key = {'key':self.key}
        pickle.dump(self_key, self_key_f)
        self_key_f.close()

        try:
            key_f = open('key', 'rb')
            key_dic = pickle.load(key_f)
            key_dic[self.name] = self.key
            key_f.close()
            key_f = open('key', 'wb')
            pickle.dump(key_dic, key_f)
            key_f.close()
        except Exception as err:
            # print(err)
            key_dic = {}
            key_dic[self.name] = self.key
            key_f = open('key', 'wb')
            pickle.dump(key_dic, key_f)
            key_f.close()

    def get_key(self):
        return self.key


class ED_Crypt:
    def __init__(self, username):
        try:
            key_f = open('key', 'rb')
            self.key = pickle.load(key_f)[username]
            key_f.close()
        except Exception as err:
            print(err)
            self.key = ''

    def encrypt(self, string):
        key = self.key
        fernet = Fernet(key)
        encrypted = fernet.encrypt(string.encode())
        return encrypted

    def decrypt(self, string):
        key = self.key
        fernet = Fernet(key)
        decrypted = fernet.decrypt(string.encode())
        return decrypted


if __name__ == "__main__":

    cr = Crypt('xg7', 'password')
    print('[Instance] Name:xg7  Pwd:password\n')
    print('[Key]', cr.get_key().decode(), '\n')

    ed = ED_Crypt('xg7')
    s0 = 'I_LOVE_ICS'
    print('[Text]', s0, '\n')
    s1 = ed.encrypt(s0).decode()
    print('[Encrypted]', s1, '\n')
    s2 = ed.decrypt(s1).decode()
    print('[Decrypted]', s2, '\n')

    a = ED_Crypt('a')
    print(a.key.decode())

    b = ED_Crypt('b')
    print(b.key.decode())
