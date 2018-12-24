#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 13:52:04

"""
Example for test esm
"""

# sys lib
import sys
from datetime import datetime

# third party lib
import esm


def esm_example():
    index = esm.Index()
    index.enter("hello")
    index.enter("world")
    index.enter("welcome")
    index.enter("me")
    index.fix()
    content = "hello world test hello me test"
    result = index.query(content)
    print("find {0} match in {1}".format(len(result), content))
    for index in range(len(result)):
        match = result[index]
        print("index:{0}, find:{1}".format(index, match))
        print("from {0} to {1} match {2}".format(match[0][0], match[0][1] - 1,
                                                 match[1]))


def esm_search_file_args(file_name, *keywords):
    keyword_list = []
    for i in range(len(keywords)):
        keyword_list.append(keywords[i])

    esm_search_file(file_name, keyword_list)


def esm_search_file(file_name, keywords):
    """
    find matches for keywods in file
    """
    print(datetime.now())
    if len(keywords) == 0:
        print("keywords number is zero.")
        return -1
    index = esm.Index()
    for i in range(len(keywords)):
        index.enter(keywords[i])
    index.fix()

    with open(file_name, "r") as read_fd:
        for line in read_fd:
            line = line.strip()
            if len(line) == 0:
                print("skip empty line")
                continue
            print("{0} has length {1}".format(line, len(line)))
            result = index.query(line)
            if len(result) == 0:
                print("find no match in {}".format(line))
                continue
            print("find {0} match in {1}".format(len(result), line))
            for i in range(len(result)):
                match = result[i]
                print("index:{0}, find:{1}".format(i, match))
                print("from {0} to {1} match {2}".format(match[0][0],
                                                         match[0][1] - 1,
                                                         match[1]))
    print(datetime.now())


def print_sys_args(sys_args):
    print("sys args type: {}".format(type(sys_args)))
    for i in range(len(sys_args)):
        print("sys_args[{0}] type is {1}".format(i, type(sys_args[i])))
        print(sys_args[i])


if __name__ == "__main__":
    # print(esm.__doc__)
    # print(esm.__file__)
    # print(esm.__name__)
    # esm_example()
    esm_search_file_args("data.txt", "hello", "test")
    print_sys_args(sys.argv)
    if len(sys.argv) >= 3:
        args = sys.argv[2:]
        esm_search_file(sys.argv[1], args)
