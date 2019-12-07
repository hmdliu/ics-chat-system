# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 17:31:04 2019

@author: Chen Xilin
"""
import os
import zipfile

def zip_compress(filename, position, pwd = None):  
    try:
        with zipfile.ZipFile(position, mode="w") as f:
            f.write(filename)
            if pwd != None:
                f.setpassword(pwd)
    except Exception as e:
        print("Error occurs")
        print("Type:%s"%type(e))
        print("Content:%s"%e)
    finally:
        f.close()

def zip_decompress(zipfile, position, pwd):
    try:
        with zipfile.ZipFile(zipfile, mode="a") as f:
             f.extractall(zipfile, pwd=pwd)
    except Exception as e:
        print("Error occurs")
        print("Type:%s"%type(e))
        print("Content:%s"%e)
    finally:
        f.close()

def zip_recrypt(zipfile, dezip_position, dezip_key, rezip_position, rezip_key):
    #decompress the file with the key of its owner(decrypted)
    zip_decompress(zipfile, dezip_position, dezip_key)
    #compress the file with the key of the requestor(encrypted)
    zip_compress(dezip_position, rezip_position, rezip_key)
    try:
        # delete the decompressed file
        os.remove(dezip_position) 
    except Exception as e:
        print("Error occurs")
        print("Type:%s"%type(e))
        print("Content:%s"%e)

