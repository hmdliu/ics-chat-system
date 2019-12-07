# -*- coding: utf-8 -*-
"""
Created on Sat Dec 7 15:47:19 2019

@author: hl3797
"""

import os
import time
from Crypt_class import *
from UserPwd_class import *

def regist():
    flag = True
    while flag:
        name = input('Please set username:')
        print()
        path = './user/' + name + '/'
        if not os.path.exists(path):
            os.makedirs(path)
            pwd = input('Please set password:')
            print()
            pwd_confirm = input('Please confirm password:')
            print()
            if pwd == pwd_confirm:
                self_crypt = Crypt(name, pwd)
                self_pwd = UserPwd(name, pwd)
                time.sleep(0.3)
                print('Registration has been created successfully.\n')
                print('=' * 47, '\n')
                flag = False
            else:
                print('Different passwords. Please regist again.\n')
                print('=' * 47, '\n')
                print_top()
                continue
        else:
            print('Username [ ' + name + ' ] has been occupied.\n')


def print_top():
    print()
    print('=' * 14, 'ICS Chat Register', '=' * 14, '\n')

def main():
    print_top()
    regist()

main()
