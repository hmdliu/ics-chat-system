# -*- coding: utf-8 -*-
"""
Created on Sat Dec 9 08:41:19 2019

@author: hl3797
"""

from ftplib import FTP

class MyFtp():
    def __init__(self):
        self.ftp_client = FTP()

    def ftp_login(self, host_ip, username, password):
        try:
            self.ftp_client.connect(host_ip, port = 2121, timeout = 3)
        except :
            print('[FTP Connect] Time out.')
            return 1001
        try:
            self.ftp_client.login(user = username, passwd = password)
        except:
            print('[FTP Connect] Username or password error.')
            return 1002
        return 1000

    def stor_file(self, filename):
        try:
            self.ftp_client.storbinary('stor ' + filename, open(filename,'rb'))
            return 1000
        except Exception as err:
            print('[FTP Stor]', err)
            return 1001

    def retr_file(self, filename):
        try:
            self.ftp_client.retrbinary('retr ' + filename, open(filename, 'wb').write)
            return 1000
        except Exception as err:
            print('[FTP Retr]', err)
            return 1001

    def get_pwd(self):

        command_result = self.ftp_client.sendcmd('pwd')
        print(command_result)

        command_result = self.ftp_client.dir()
        print(command_result)

    def ftp_logout(self):
        # print('Disconnect with the server.')
        self.ftp_client.close()

if __name__ == '__main__':

    host_ip = 'localhost'
    username = 'a'
    password = 'ew5HWFVHKsYSf3ZSBzs6PaEE2gbe7XMbTLikwR-Sbkc='

    my_ftp = MyFtp()

    if my_ftp.ftp_login(host_ip, username, password) == 1000:
        print('Login success.')
        my_ftp.get_pwd()
        my_ftp.stor_file('indexer.py')
        my_ftp.ftp_logout()
