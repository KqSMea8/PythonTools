#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-25 17:52:04

import sys
import os
import ConfigParser
import logging
import pexpect
import pxssh

def download(server, filename):
    cf = ConfigParser.ConfigParser()
    cf.read("config.conf")
    server_ip = cf.get(server, "ip")
    server_port = cf.get(server, "port")
    user_name = cf.get(server, "username")
    password = cf.get(server, "password")
    remote_dir = cf.get(server, file)
    passwd_key = '.*assword:'
    scp_str = "scp -P %s %s@%s:%s/%s %s/%s"
    root_dir = cf.get("system", "project_root")
    download_dir = cf.get("system", "download_path")
    local_dir = root_dir + os.path.sep + download_dir
    cmd_line = scp_str % (server_port, user_name, server_ip, remote_dir, filename, local_dir, server + "_" + filename)
    logging.warn("cmd_line: %s" % cmd_line)
    try:
        child = pexpect.spawn(cmd_line, timeout=300)
        child.logfile = sys.stdout
        child.expect(passwd_key)
        child.sendline(password)
        child.expect(pexpect.EOF)
        logging.warn("finish download %s from %s" % (filename, server))
    except Exception as e:
        logging.error("download %s from %s failed,error: %s" %(filename, server, e))

def get_full_download_file_path(filename):
    cf = ConfigParser.ConfigParser()
    cf.read("config.conf")
    root_dir = cf.get("system", "project_root")
    download_dir = cf.get("system", "download_path")
    local_dir = root_dir + os.path.sep + download_dir
    full_file_path = local_dir + os.path.sep + filename

    return full_file_path


