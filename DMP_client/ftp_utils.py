#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-17 12:05:03

import os
import socket
import ftplib
from ftplib import FTP #import the ftp module

def connect_ftp(host, port, user_name, password):
    ftp = FTP()
    ftp.set_debuglevel(0)
    try:
        ftp.connect(host, port)
    except (socket.error, socket.gaierror):
        print 'ERROR: cannot connect to {0}:{1}'.format(host, port)
        return None
    try:
        ftp.login(user_name, password)
    except ftplib.error_perm:
        print 'ERROR: cannot login with user {0} and password {1}'.format(user_name, password)
        ftp.quit()
        return None

    return ftp

def close_ftp(conn):
    conn.close()

def uploadfile(conn, filename):
    """
    conn is the connection to the ftp server
    Upload specified file to the ftp server
    """
    result = -1
    with open(filename, "rb") as readfd:
        ret = conn.storbinary("STOR " + filename, readfd)
        print(ret)
        ret_code = ret[0:3]
        if (ret_code.isdigit() and int(ret_code) == 226):
            print("upload {0} success".format(filename))
            result = 0
        else:
            print("upload {0} failed".format(filename))
    return result

def downloadfile(conn, ftp_path, local_path="."):
    """
    conn is the connection to the ftp server
    Download specified file to the ftp server
    """
    ftp_path = ftp_path.rstrip('/')
    try:
        if ftp_path not in conn.nlst(os.path.dirname(ftp_path)):
            print('ERROR: ftp file {0} not exist'.format(ftp_path))
            return -1
    except ftplib.error_perm, e:
        return -1

    file_name = os.path.basename(ftp_path)
    if os.path.isdir(local_path):
        file_handler = open(os.path.join(local_path, file_name),'wb')
        conn.retrbinary("RETR %s" %(ftp_path), file_handler.write)
        file_handler.close()
    elif os.path.isdir(os.path.dirname(local_path)):
        file_handler = open(local_path, 'wb' )
        conn.retrbinary("RETR %s" %(ftp_path), file_handler.write)
        file_handler.close()
    else:
        print 'EROOR:The dir:%s is not exist' %os.path.dirname(local_path)
        return -1

    return 0

