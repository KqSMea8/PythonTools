#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-27 10:46:06

"""
This script is test the ftplib function
"""
import os
import sys
import socket
import ftplib
from ftplib import FTP #import the ftp module
import subprocess
import time

def uploadfile(host, port, user_name, password, filename):
    """
    Upload specified file to the ftp server
    """
    ftp = FTP()
    ftp.set_debuglevel(0)
    try:
        ftp.connect(host, port)
    except (socket.error, socket.gaierror):
        print 'ERROR: cannot connect to {0}:{1}'.format(host, port)
        return -1
    try:
        ftp.login(user_name, password)
    except ftplib.error_perm:
        print 'ERROR: cannot login with user {0} and password {1}'.format(user_name, password)
        ftp.quit()
        return -1
    result = -1
    with open(filename, "rb") as readfd:
        ret = ftp.storbinary("STOR " + filename, readfd)
        print(ret)
        ret_code = ret[0:3]
        if (ret_code.isdigit() and int(ret_code) == 226):
            print("upload {0} success".format(filename))
            result = 0
        else:
            print("upload {0} failed".format(filename))
    ftp.quit()
    return result

def main(filename):
    """
    This is the main function that compress the file, compare with the old file,
    if new file is different from the old file than upload it.
    filename is the output of the dump host py, for example: 10040
    """
    host = "192.168.56.103"
    port = 21
    user_name = "linus_dev"
    password = "dev"
    # gzip compress
    res = subprocess.Popen("ls | grep keys.{0} | grep gz | grep -v md5".format(filename),stdout=subprocess.PIPE,shell=True)
    zipfile_name_list = res.stdout.readlines()
    count = len(zipfile_name_list)
    if (count > 1):
        print "ERROR, Has more than one file for the key {0}".format(filename)
        exit(-1)

    now = time.strftime("%Y%m%d%H%M")
    print now
    curr_zipfile = "keys.{0}.{1}.gz".format(filename, now)
    curr_zipfile = curr_zipfile.strip()
    md5_name = curr_zipfile+".md5"

    res = subprocess.Popen("gzip -n  %s" % filename,
                           stdout=subprocess.PIPE, shell=True)
    retcode = res.wait()
    if (retcode != 0):
        print "Popen failed"
        exit(-1)
    orig_file = filename+".gz"
    os.rename(orig_file, curr_zipfile)

    res = subprocess.Popen("md5sum %s | awk '{print $1}'" % curr_zipfile, stdout=subprocess.PIPE,shell=True)
    md5lines = res.stdout.readlines()
    md5 = md5lines[0].strip()
    print md5

    if count == 1:
        pre_zipfile=zipfile_name_list[0].strip()
        print pre_zipfile
        cmd="cmp %s %s" % (pre_zipfile,curr_zipfile)
        res = subprocess.Popen(cmd.strip(), stdout=subprocess.PIPE,shell=True)
        retcode = res.wait()
        cmp_result=res.stdout.readlines()
        count = len(cmp_result)
        if (count==0):
            print "same"
            os.remove(curr_zipfile)
            exit(-1)
        else:
            os.remove(pre_zipfile)
            os.remove(pre_zipfile+".md5")
            open(md5_name, 'w').write(md5)
    else:
        open(md5_name, 'w').write(md5)


    retcode = uploadfile(host, port, user_name, password, curr_zipfile)
    if (retcode != 0):
        os.remove(curr_zipfile)
        os.remove(md5_name)
        return -1
    retcode = uploadfile(host, port, user_name, password, md5_name)
    if (retcode != 0):
        os.remove(curr_zipfile)
        os.remove(md5_name)
        return -1

if __name__=='__main__':
    if (len(sys.argv) != 2):
        print "Usage {0} <filename>".format(sys.argv[0])
    main(sys.argv[1])
