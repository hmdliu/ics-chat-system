# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:40:00 2019

@author: hl3797
"""
import pickle
from random import choice

DICT = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
CONFUSE = [ch for ch in DICT]

class UserPwd:
    def __init__(self, name, pwd):
        self.name = name
        self.path = './user/' + name + '/' + name + '.pwd'
        self.pwd = self.generate_pwd(pwd)
        self.save_data()

    def get_length(self, pwd):
        # Set the length of meaningless string
        t = 0
        for ch in pwd:
            if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z':
                t += ord(ch)
        t = t // len(pwd)
        # print('t =', t)
        return t

    def get_string(self, length):
        # Generate a meaningless string
        global CONFUSE
        s = ''
        for i in range(length):
            s += choice(CONFUSE)
        return s

    def generate_pwd(self, pwd):
        # Generate a confused password
        global CONFUSE
        ans = ''

        for ch in pwd[::-1]:
            ans += choice(CONFUSE) + ch

        t = self.get_length(pwd)
        ans = self.get_string(t) + ans + self.get_string(t)
        # print('Ans:', ans)
        return ans

    def save_data(self):
        # Dump confused data
        pwd_f = open(self.path, 'wb')
        # dic = {self.name:self.pwd}
        pickle.dump(self, pwd_f)

    def check_pwd(self, input_pwd):
        # Check login password
        try:
            t = self.get_length(input_pwd)
            # pwd_f = open(self.path, 'rb')
            # pickle.load(pwd_f)
            pwd = self.pwd[t:-t][::-2]
            return True if input_pwd == pwd else False
        except Exception as err:
            return False

if __name__ == "__main__":
    pwd = UserPwd('Name', 'password')
    print(pwd.check_pwd('password'))
    print(pwd.check_pwd('Password'))
