#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: my_thread.py.py
@time: 2017/7/24 14:27
"""

from __future__ import print_function

import logging
import sys
import threading
import time


class MyThread(threading.Thread):
    """
    define self Thread class to meet the requirement
    """

    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.res = None

    def run(self):
        logging.info("starting %s at: %s" % (self.name, time.ctime()))
        self.res = self.func(*self.args)
        logging.info("finished %s at: %s" % (self.name, time.ctime()))

    def get_result(self):
        return self.res


def flush_dict_to_file(data, save_file_name, sep=","):
    """
    The function flush the content in dict data to file save_file_name
    
    :param data: the dict want to save to file
    :param save_file_name: the file name used to save the dict
    :param sep: the separator between the key and value
    :return: None
    """
    with open(save_file_name, mode='rw') as writer:
        for key, value in enumerate(data):
            print("{0}{1}{2}".format(key, sep, value), file=writer)


def flush_list_to_file(data, save_file_name):
    """
    The function flush the content in list data to file save_file_name

    :param data: the list want to save to file
    :param save_file_name: the file name used to save the dict
    :return: None
    """
    with open(save_file_name, mode='rw') as writer:
        for key in data:
            print("{0}".format(key), file=writer)


def display_dict(data, sep=","):
    """
    display the content of the dict
    :param data: the dict want to display
    :param sep: the separator between the key and value
    :return: None
    """
    flush_dict_to_file(data, save_file_name=sys.stdout, sep=sep)


def display_list(data):
    """
    display the content of the list
    :param data: the dict want to display
    :return: None
    """
    flush_dict_to_file(data, save_file_name=sys.stdout)
