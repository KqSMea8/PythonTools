#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-01 10:15:45

from __future__ import print_function
import sys
import os
import logging
import esm

"""
解析rtb_notice日志，获取过滤的域名计数统计，并按照被过滤数量从大到小排序，相当于下面这个awk脚本的功能
cat rtb_log_notice_* | awk -F '\1' '{if(length($23) > 0) a[$23]++}END{for(i in a)print(i, a[i])}' | sort -nrk2 | more
"""


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="filter_domain.log",
                        filemode="a")


def get_file_list(dir_name, filters_list):
    if dir_name is None or len(dir_name) == 0:
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = set()
    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                result = index.query(filename)
                if len(result) == len(filters_list):
                    files.add(os.path.join(parent, filename))
    else:
        if len(index.query(dir_name)) == len(filters_list):
            files.add(dir_name)

    return files


def get_filter_domain(domain_dict, file_name):
    with open(file_name, 'r') as read_fd:
        for line in read_fd:
            line = line.strip()
            segs = line.split('\1')
            domain_dict.setdefault(segs[22],0)
            domain_dict[segs[22]] = domain_dict[segs[22]] + 1


if __name__ == '__main__':
    init_logging()
    if len(sys.argv) < 3:
        print("Usage {} <log dir> <out_file_name> [filter_strs]".format(sys.argv[0]))
        exit(-1)

    filters=[]
    if len(sys.argv)>3:
        filters = sys.argv[3:]
        logging.info("file name filter: {0}".format(filters))

    files = get_file_list(sys.argv[1], filters)
    if files is None:
        print("file list is None")
        exit(-1)

    domain_dict={}
    assert(isinstance(files, set))
    for file in files:
        #print("file: {}".format(file))
        if file.find("notice") != -1:
            get_filter_domain(domain_dict, file)

    # sorted according to the value of the dict
    # explain the code:
    # domain_dict.items used to acquire the list of the (key, value) tuple
    # then use sorted function, through the parameter key: specify the sort
    # is according the value, that is second value of the tuple: d[1], reverse
    # is set to True mean the result need to reversed, default is from little
    # to big.
    sorted_dict=sorted(domain_dict.items(), key=lambda d:d[1], reverse = True)

    # next is sorted according to the key of the dict
    # sorted_dict=sorted(domain_dict.items(), key=lambda d:d[0], reverse = True)
    with open(sys.argv[2], 'w') as writefd:
        for item in sorted_dict:
            writefd.write("domain: {0}, times: {1}\n".format(item[0], item[1]))
