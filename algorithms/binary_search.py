#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 11:38
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : binary_search.py
# @Software: PyCharm
# @Description 二分查找

import sys
import logging
from datetime import datetime, timedelta


def get_delta_time(now, past):
    """
    the parameter now and past is the datetime type
    this function return the delta time between this two time
    timedelta's total_seconds function return the seconds in the duration
    this function return the time in microseconds
    """
    timespan = now - past
    attrs = [("days", "日"), ("seconds", "秒"), ("microseconds", "毫秒")]
    for k, v in attrs:
        "timespan.{0} = {1} #{2}".format(k, getattr(timespan, k), v)
    return timespan.total_seconds() * 1e6


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:\
                                %(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="show.log",
                        filemode="a")


def binary_search(key, data):
    low = 0
    high = len(data) - 1
    while low <= high:
        mid = (low + high) / 2
        cmp_value = cmp(key, data[mid])
        print("key {0}, data[{1}]:{2}, cmp_value {3}, high {4} low {5}".format(key, mid,
                                                                               data[mid], cmp_value, high, low))
        if cmp_value < 0:
            high = mid - 1
        elif cmp_value > 0:
            low = mid + 1
        else:
            return mid

    return -1


def init_data(file_name, data):
    with open(file_name, mode="r") as readfd:
        for line in readfd:
            data.append(line.strip())


if __name__ == "__main__":
    data = list()
    init_data(sys.argv[1], data)
    data.sort()
    """
    for key in data:
        print(key)
    """
    while (True):
        key = raw_input("Please enter the search key: ")
        past = datetime.now()
        index = binary_search(key, data)
        # index = data.index(key)
        now = datetime.now()
        print("use time {0} for search {1}".format(get_delta_time(now, past),
                                                   key))
        if (index == -1):
            print("Can't find the key {0}".format(key))
        else:
            print("The index for the key {0} is {1}".format(key, index))
