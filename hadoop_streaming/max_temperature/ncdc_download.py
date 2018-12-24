#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-20 17:13:10

import sys
import os
from ftplib import FTP

# ftp connection
def ftpconnect():
    ftp_server="ftp.ncdc.noaa.gov"
    username=''
    password=''
    ftp=FTP()
    ftp.set_debuglevel(2)
    ftp.connect(ftp_server, 21)
    ftp.login(username, password)

    return ftp

def downloadfile():
    ftp = ftpconnect()
    print ftp.getwelcome()

    datapath="/pub/data/noaa/isd_lite/"
    year=int(sys.argv[1])
    currentyear=year
    while (year <= int(sys.argv[2])):
        path=datapath+str(year)
        li=ftp.nlst(path)

        path=sys.argv[3]+"/"
        dir=str(year)
        new_path=os.path.join(path,dir)
        if not os.path.isdir(new_path):
            os.makedirs(new_path)

        for eachFile in li:
            localpaths = eachFile.split("/")
            localpath=localpaths[len(localpaths)-1]
            localpath=new_path + "/" + str(year)+"--"+localpath
            bufsize=1024
            fp=open(localpath, 'wb')
            ftp.retrbinary('RETR ' + eachFile, fp.write, bufsize)
        year=year+1
    ftp.set_debuglevel(0)
    fp.close()
    ftp.quit()

if __name__=='__main__':
    downloadfile()
