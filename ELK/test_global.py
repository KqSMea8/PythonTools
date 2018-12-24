#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: test_global.py.py
@time: 08/11/2017 14:23
"""

import threading
import time
import sys

curr_time = 0


def timer_func(interval):
    while True:
        print "curr_time in timer_func: %d" % int(curr_time)
        remaining = interval - int(curr_time) % interval
        time.sleep(remaining)


if __name__ == '__main__':
    print len(sys.argv)
    t = threading.Thread(target=timer_func, args=(5,))
    t.start()
    while True:
        print "curr_time in main: %d" % int(curr_time)
        curr_time += 5
        time.sleep(5)