#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 11:37
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : socket_program.py
# @Software: PyCharm
# @Description socket程序

from __future__ import print_function

import socket
import time
import sys
import os
import string

"""
This is a socket program example.
The code is from or change from <Core Python Programming>
"""


def create_tcp_server(host="", port=12345):
    BUFSIZE = 1024
    ADDR = (host, port)

    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSerSock.bind(ADDR)
    tcpSerSock.listen(5)

    while True:
        print("Waiting for connection...")
        tcpCliSock, addr = tcpSerSock.accept()
        print("...connected from: %s:%d" % (addr[0], addr[1]))

        while True:
            data = tcpCliSock.recv(BUFSIZE)
            if not data:
                break

            tcpCliSock.send("[%s] %s" % (time.ctime(), data))

        tcpCliSock.close()

    tcpSerSock.close()


def create_tcp_client(host, port):
    BUFSIZE = 1024
    ADDR = (host, port)

    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.connect(ADDR)

    while True:
        data = raw_input(">")
        if not data:
            break;

        tcpCliSock.send(data)
        data = tcpCliSock.recv(BUFSIZE)
        if not data:
            break;

        print("recv from server is: " + data)

    tcpCliSock.close()


# first check the input argument
if 4 != len(sys.argv):
    print("Usage: " + os.path.basename(sys.argv[0]) + " <server/client> <host> <port>")
    mode = raw_input("Please enter the tcp socket mode<server/client>:\n")
    host = raw_input("Please enter the host of the socket:\n")
    port = raw_input("Please enter the port of the socket:\n")
else:
    mode = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]

port = string.atoi(port)
print("port is %d" % port)

if (0 == cmp(mode, "server")):
    create_tcp_server(host, port)
elif (0 == cmp(mode, "client")):
    create_tcp_client(host, port)
else:
    print("Wrong mode. Please use server or client")
