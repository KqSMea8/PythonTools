#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: get_filter_domain.py
@time: 12/12/2017 16:31
"""

from __future__ import print_function
import sys
import os
import logging
import esm


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="filter_domain.log",
                        filemode="a")


def get_file_list(dir_name, filters_list):
    if (None == dir_name or 0 == len(dir_name)):
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    if (os.path.isdir(dir_name)):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                result = index.query(filename)
                if (len(result) == len(filters_list)):
                    files.append(os.path.join(parent, filename))
    else:
        if (len(index.query(dir_name)) == len(filters_list)):
            files.append(dir_name)

    return files


def get_filter_domain(domain_dict, file_name):
    print("file: {0}".format(file_name))
    with open(file_name, 'r') as read_fd:
        for line in read_fd:
            line = line.strip();
            segs = line.split('\1')
            domain_dict.setdefault(segs[22],0)
            domain_dict[segs[22]] = domain_dict[segs[22]] + 1


if __name__ == '__main__':
    init_logging()
    if len(sys.argv) < 3:
        print("Usage {0} <log dir> <out_file_name> [filter_strs]".format(sys.argv[0]))
        exit(-1)

    filters=[]
    if (len(sys.argv)>3):
        filters = sys.argv[3:]
        logging.info("file name filter: {0}".format(filters))

    files = get_file_list(sys.argv[1], filters)
    domain_dict={}
    for file in files:
        #print("file: {}".format(file))
        if (file.find("notice") != -1):
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
    #sorted_dict=sorted(domain_dict.items(), key=lambda d:d[0], reverse = True)
    with open(sys.argv[2], 'w') as writefd:
        for item in  sorted_dict:
            writefd.write("domain: {0}, times: {1}\n".format(item[0], item[1]))