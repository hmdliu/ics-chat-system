# -*- coding: utf-8 -*-
"""
Created on Sat Dec 7 17:31:04 2019

@author: Chen Xilin, hl3797
"""
import os
from shutil import copy

PROJECT_PATH = './'

def zip_compress(path, filename, pwd, delete = False):
    try:
        os.chdir(path)
        # print(os.getcwd())
        if not os.path.exists(filename):
            return 1002
        cmd = "zip -P %s -r %s %s" % (pwd, filename + '.zip', filename)
        status = os.system(cmd)
        if status != 0:
            raise Exception('Zip Error')
        if delete:
            os.remove(filename)
        os.chdir(PROJECT_PATH)
        return 1000
    except Exception as err:
        print('[Zip Compress]', err)
        print('Notes:Please install zip & unzip in cmd.\n')
        return 1001

def zip_decompress(path, zip_name, pwd, delete = False):
    try:
        os.chdir(path)
        if not os.path.exists(zip_name):
            return 1002
        cmd = "unzip -P %s %s" % (pwd, zip_name)
        status = os.system(cmd)
        if status != 0:
            raise Exception('Unzip Error')
        if delete:
            os.remove(zip_name)
        os.chdir(PROJECT_PATH)
        return 1000
    except Exception as err:
        print('[Zip Decompress]', err)
        print('Notes:Please install zip & unzip in cmd.\n')
        return 1001

def zip_recrypt(zip_path, to_path, zip_name, pwd1, pwd2):
    try:
        copy(zip_path + zip_name, to_path)
        os.chdir(to_path)
        # decompress the file with the key of its owner(decrypted)
        status_code = zip_decompress('./', zip_name, pwd1, True)
        # print('[Recryption] Zip D', status_code)
        # compress the file with the key of the requestor(encrypted)
        if status_code == 1000:
            status_code = zip_compress(to_path, zip_name.replace('.zip', ''), pwd2, True)
            # print('[Recryption] Zip C', status_code)
        os.chdir(PROJECT_PATH)
        return status_code
    except Exception as err:
        print('[Zip Recryption]', err)
        print('Notes:Please install zip & unzip in cmd.\n')
        return 1001


if __name__ == "__main__":

    input('[Zip Demo]:\n\nPress enter to Zip 1.txt:')
    print()

    zip_compress('./', '1.txt', '111', True)

    input('Zip finished, press enter to Unzip:')
    print()

    zip_decompress('./', '1.txt.zip', '111', False)

    # zip_recrypt('./demo/', './user/', 'aaa.txt.zip', '111', '222')
