#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: tools.py
@time: 2017/3/30 下午9:54
"""

import os
import sys
import random

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage python tools.py <filename> <line number>"
        sys.exit(0)

    file_name = sys.argv[1]
    line_number = int(sys.argv[2])
    selected_lines = list()
    selected_count = 0
    select_content = list()
    rand = random.Random()
    full_filename = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + file_name
    with open(full_filename, mode='r') as fd:
        contents = fd.readlines()
        max_line_index = len(contents) - 1
        while True:
            number = rand.randint(0, max_line_index)
            if number not in selected_lines:
                selected_lines.append(number)
                selected_count += 1

            if selected_count >= line_number:
                break

        select_content = [contents[i].strip() for i in selected_lines]

    # for i in selected_lines:
    #    print i
    for line in select_content:
        print line
