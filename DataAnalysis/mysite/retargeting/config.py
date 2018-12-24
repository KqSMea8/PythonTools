#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: config.py
@time: 2017/7/25 16:22
"""

from ConfigParser import ConfigParser

conf = ConfigParser()
conf.read("conf/config.ini")


def get_int_value(section, option):
    return conf.getint(section=section, option=option)


def get_value(section, option):
    return conf.get(section=section, option=option)

