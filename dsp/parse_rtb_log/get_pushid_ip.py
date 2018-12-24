#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-24 13:43:48

"""
This script is used to parse bidder log to get the pushid and the correspoding
ip
print() is python 3.x built-in function, while in python < 3.x print is a
operator
if you want to use print function, should use 'from __future__ import
print_function'
"""

from __future__ import print_function
import string
import sys
import os
import logging
import time
import esm

import threading


class MyThread(threading.Thread):
    """
    define self Thread class to meet the requirement
    """
    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        #logging.info("starting %s at: %s" % (self.name, time.ctime()))
        self.res = self.func(*self.args)
        #logging.info("finished %s at: %s" % (self.name, time.ctime()))

    def getResult(self):
        return self.res

def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="show.log",
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

def generate_file(adid, pushid_ip_dict, file_name, filter_str):
    """
    generate the pushid from the file specified by file_name which ad id is
    equvalent to the adid
    the filter_str can be bid,bidres,rtb_creative,rtb_show,rtb_click now
    rtb_noAd and rtb_visit don't have pushid
    """
    if (None == pushid_ip_dict or None == file_name or 0 == len(file_name)):
        return

    #print("filter = " + id_filter)
    #filter *.tar.gz
    if (-1 != string.find(file_name, ".tar.gz")):
        return

    if (not os.path.isfile(file_name)):
        print(file_name + " is not a file!")
    else:
        if (not string.find(file_name, "rtb_log_crit_", 0, len("rtb_log_crit_"))):
            print(file_name + " is not rtb_log_crit log file")
            return
        with open(file_name) as fd:
            for line in fd:
                strs = string.split(line, sep="\1")
                strs[0] = string.strip(strs[0])
                if (0 != cmp(strs[0], filter_str) or 0 != cmp(strs[6], adid)):
                    #print("compare result of {0} and {1} is {2}".format(strs[0],
                    #    filter_str, cmp(strs[0], filter_str)))
                    #print("compare result {0} and {1} is {2}".format(strs[6],
                    #    adid, cmp(strs[6], adid)))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != rtb_show")
                    continue
                else:
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    #print("key: {0}".format(key))
                    #strs[7] is pushid, strs[8] is ip
                    key=strs[7]
                    pushid_ip_dict.setdefault(key, None)
                    if pushid_ip_dict[key] == None:
                        value=set()
                        value.add(strs[8])
                        pushid_ip_dict[key]=value
                    else:
                        pushid_ip_dict[key].add(strs[8])
    #logging.info("[generate_pushid_file]finish parse file: " + file_name)

def generate_thread(ad_id, file_list, filter_str):
    """
    generate the pushid list
    """

    if (None == file_list or 0 == len(file_list)):
        return

    pushid_ip_dict = dict()
    for file_name in file_list:
        generate_file(ad_id, pushid_ip_dict, file_name, filter_str)

    return pushid_ip_dict

def print_pushid_ip_dict(pushid_ip_dict):
    for key in pushid_ip_dict.keys():
        print("{0}:{1}".format(key,pushid_ip_dict[key]))

def flush_pushid_ip_dict(pushid_ip_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for key in pushid_ip_dict.keys():
            print("{0}:{1}".format(key,pushid_ip_dict[key]), file=outfd)

def merge_dict(orig_dict, add_dict):
    """
    This function merge the two dict, add the add_dict to orig_dict. The value must be
    numeric
    merge method:
        the result dict will hold both keys in this two dict, if a key in both
        dict, than the value will be added
    """
    for key in add_dict.keys():
        if orig_dict.has_key(key):
            orig_dict[key].update(add_dict[key])
        else:
            orig_dict[key]=add_dict[key]

FILES_PER_THREAD = 100

if __name__ == "__main__":
    init_logging()
    #file_name=raw_input("Please enter the file name: ");
    #print_file(file_name);
    """
    This dict's structure is as below:
    The key is adid, value is pushid
    """
    pushid_ip_dict = dict()
    out_dir = ""
    print(sys.argv)
    #first check the input argument
    if (len(sys.argv) < 4):
        print("Usage: " + os.path.basename(sys.argv[0]) + " <log_dir_name> <adid> <out_dir_name>")
        log_dir_name = raw_input("Please enter the directory name of the log file:\n")
        adid = raw_input("Please enter the adid to analysis:\n")
        out_dir = raw_input("Please enter the out put directory:\n")
    else:
        log_dir_name = sys.argv[1]
        adid = sys.argv[2]
        out_dir = sys.argv[3]

    filters = [""]
    if (len(sys.argv) > 4):
        filters = sys.argv[4:]
        logging.info("file name filter: {0}".format(filters))

    if out_dir[len(out_dir) - 1] != os.path.sep:
        out_dir = out_dir + os.path.sep

    if (not os.path.isdir(out_dir)):
        print("out directory is null!")
        out_dir = ""

    file_list = get_file_list(log_dir_name, filters)
    logging.info("number of log file is %d" % len(file_list))
    pushid_file = out_dir + "pushid.txt"
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if ((len(file_list) % FILES_PER_THREAD) != 0):
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(generate_thread, (adid, file_list[i *
            FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD], "rtb_bidres"),
            generate_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(generate_thread, (adid, file_list[(thread_num - 1) *
        FILES_PER_THREAD: len(file_list)], "rtb_bidres"),
        generate_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        temp_dict = threads[i].get_result()
        logging.info("len of {0} temp_dict is {1}".format(threads[i].getName(),
            len(temp_dict.keys())))
        merge_dict(pushid_ip_dict, temp_dict)

    logging.info("total pushid ip num: {0}".format(len(pushid_ip_dict.keys())))
    flush_pushid_ip_dict(pushid_ip_dict, pushid_file)

    error_pushid_file=out_dir + "error_pushid.txt"
    error_pushid_dict=dict()
    for key in pushid_ip_dict:
        if (len(pushid_ip_dict[key]) > 1):
            error_pushid_dict[key]=pushid_ip_dict[key]

    flush_pushid_ip_dict(error_pushid_dict, error_pushid_file)
