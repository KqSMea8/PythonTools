#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 11:09:59

"""
Example of register shutdown function
"""

import atexit
import time
import math

def microtime(get_as_float=False):
    if get_as_float:
        return time.time()
    else:
        return "%f %d" % math.modf(time.time())

start_time = microtime(False)
atexit.register(start_time)

def shutdown():
    global start_time
    print("Execution took: {0} seconds".format(start_time))

atexit.register(shutdown)
