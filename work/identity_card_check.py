#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-13 11:40:13

"""
This script calculate the validate num for the ID card
use the check_id function to check the ID is valid or not
"""

import time

WEIGHT = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
VALIDATE = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']


def get_validate_code(id_str):
    sum_value = 0
    mode = 0
    for i in range(17):
        sum_value += int(id_str[i]) * WEIGHT[i]

    mode = sum_value % 11
    return VALIDATE[mode]


def load_area_code(area_code_file):
    """
    This function load the area code from csv file
    """
    area_code_set = set()
    with open(area_code_file, "r") as readfd:
        for line in readfd:
            line = line.strip()
            area_code_str = line.split(",")[0]
            if area_code_str.isdigit():
                area_code = int(area_code_str)
                area_code_set.add(area_code)

    return area_code_set


def check_date(year, month, day):
    month_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_str = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"]
    if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
        month_day[1] = 29

    current = time.localtime()
    if (year > current.tm_year) or (year == current.tm_year and month > current.tm_mon) or (
            year == current.tm_year and month > current.tm_mon and day > current.tm_mday):
        print "The time is before now"
        return False

    if day > month_day[month - 1]:
        print "The day is invalid, the %s has no day %d" % (month_str[month - 1], day)
        return False

    return True


def check_id(id_str):
    """
    This function check Identity code is valid or not
    """
    if len(id_str) != 18:
        print "The ID length is invalid"
        return False
    area_code_set = load_area_code("area_code.csv")
    area_code = int(id_str[0:6])
    if not area_code in area_code_set:
        print "area code error"
        return False

    year = int(id_str[6:10])
    month = int(id_str[10:12])
    day = int(id_str[12:14])
    if check_date(year, month, day) is not True:
        print "date is invalid"
        return False

    if id_str[17] != get_validate_code(id_str[:17]):
        print "validate code is invalid"
        return False

    return True


if __name__ == '__main__':
    print "The validate code of the ID card is %s" % get_validate_code("33012219870704221")
    while True:
        ID_STR = raw_input("Please enter a ID code: ")
        RET = check_id(ID_STR)
        if RET is True:
            print "The ID is valid"
        else:
            print "The ID invalid"
