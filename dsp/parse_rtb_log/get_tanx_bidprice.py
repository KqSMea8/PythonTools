#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-15 09:05:29

"""
This script will parse the bidder log and get the bidder price corresponding to every ad_space and host
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
                        filename="adspace_bidprice.log",
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
                if (len(result) != len(filters_list)):
                    files.append(os.path.join(parent, filename))
    else:
        if (len(index.query(dir_name)) == len(filters_list)):
            files.append(dir_name)

    return files
	
def generate_pushid_file(adid, pushid_bidprice_dict, file_name, filter_str):
    """
    generate the pushid and corresponding bidprice from the file specified
    by file_name which ad id is equvalent to the adid
    the filter_str can be bid,bidres,rtb_creative,rtb_show,rtb_click now
    rtb_noAd and rtb_visit don't have pushid
    """
    if (None == pushid_bidprice_dict or None == file_name or 0 == len(file_name)):
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
                    #    "rtb_show", cmp(strs[0], "rtb_show")))
                    #print("compare result {0} and {1} is {2}".format(strs[6],
                    #    adid, cmp(strs[6], adid)))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != rtb_show")
                    continue
                else:
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    if (float(strs[9]) > 10.0 or float(strs[9]) < 0.0):
                        logging.warning("pushid: {0}, bidprice: {1}. bidprice error.".format(strs[7],strs[9]))
                        continue
                    pushid_bidprice_dict[strs[7]] = strs[9]
    #logging.info("[generate_pushid_file]finish parse file: " + file_name)

def generate_pushid_thread(ad_id, file_list, filter_str):
    """
    generate the pushid bidprice dict
    """

    if (None == file_list or 0 == len(file_list)):
        return

    pushid_bidprice_dict = dict()
    for file_name in file_list:
        generate_pushid_file(ad_id, pushid_bidprice_dict, file_name, filter_str)

    return pushid_bidprice_dict

def print_pushid_bidprice_dict(pushid_bidprice_dict):
    for pushid in pushid_bidprice_dict.keys():
        print("{0}:{1}".format(pushid, pushid_bidprice_dict[pushid]))

def flush_pushid_bidprice_dict(pushid_bidprice_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for pushid in pushid_bidprice_dict.keys():
            print("{0}:{1}".format(pushid, pushid_bidprice_dict[pushid]), file=outfd)


def get_adspace_file(adid, pushid_bidprice_dict, file_name, filter_str, adspace_bidprice_dict):
    """
    get the adspace from the file specified by file_name which ad id is equvalent to the adid
    and pushid is in the pushid_bidprice_dict
    the filter_str can be bid,bidres,rtb_creative,rtb_show,rtb_click now
    rtb_noAd and rtb_visit don't have pushid
    """
    if (None == pushid_bidprice_dict or None == file_name or 0 == len(file_name)):
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
                if (0 != cmp(strs[0], filter_str) or 0 != cmp(strs[6], adid) or strs[7] not in pushid_bidprice_dict):
                    #print("compare result of {0} and {1} is {2}".format(strs[0],
                    #    "rtb_show", cmp(strs[0], "rtb_show")))
                    #print("compare result {0} and {1} is {2}".format(strs[6],
                    #    adid, cmp(strs[6], adid)))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != rtb_show")
                    continue
                else:
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    if not strs[24] in adspace_bidprice_dict:
                        adspace_bidprice_dict[strs[24]] = list()
                    adspace_bidprice_dict[strs[24]].append(str(pushid_bidprice_dict[strs[7]]))
    #logging.info("[generate_pushid_file]finish parse file: " + file_name)

def get_adspace_thread(ad_id, pushid_bidprice_dict, file_list, filter_str):
    """
    according to the pushid_bidprice_dict, generate the log file, get the
    corresponding adspace
    """

    if (None == file_list or 0 == len(file_list)):
        return

    # the key is the adspace, the value is the bidprice
    adspace_bidprice_dict = dict()
    for file_name in file_list:
        get_adspace_file(ad_id, pushid_bidprice_dict, file_name, filter_str, adspace_bidprice_dict)

    return adspace_bidprice_dict

def print_adspace_bidprice_dict(adspace_bidprice_dict):
    for pushid in adspace_bidprice_dict.keys():
        value = ",".join(adspace_bidprice_dict[pushid])
        print("{0}:{1}".format(pushid, value))

def flush_adspace_bidprice_dict(adspace_bidprice_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for pushid in adspace_bidprice_dict.keys():
            value = ",".join(adspace_bidprice_dict[pushid])
            print("{0}:{1}".format(pushid, value), file=outfd)

def merge_adspace_bidprice_dict(orig_dict, temp_dict):
    for temp_key in temp_dict.keys():
        if temp_key in orig_dict:
            orig_dict[temp_key].extend(temp_dict[temp_key])
        else:
            orig_dict[temp_key] = temp_dict[temp_key]


FILES_PER_THREAD = 10

if __name__ == "__main__":
    init_logging()

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


    if out_dir[len(out_dir) - 1] != os.path.sep:
        out_dir = out_dir + os.path.sep

    if (not os.path.isdir(out_dir)):
        print("out directory is null!")
        out_dir = ""

    # Get the file list need to parse
    filters = [""]
    if (len(sys.argv) > 4):
        filters = sys.argv[4:]
        logging.info("file name filter: {0}".format(filters))

    file_list = get_file_list(log_dir_name, filters)
    logging.info("number of log file is %d" % len(file_list))

    pushid_bidprice_file = out_dir + "pushid_bidprice.txt"
    adspace_bidprice_file = out_dir + "adspace_bidprice.txt"

    # Get the pushid and bidprice that has bidres, means we have succeed in bid
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if ((len(file_list) % FILES_PER_THREAD) != 0):
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(generate_pushid_thread, (adid, file_list[i *
            FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD], "rtb_bidres"),
            generate_pushid_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(generate_pushid_thread, (adid, file_list[(thread_num - 1) *
        FILES_PER_THREAD: len(file_list)], "rtb_bidres"),
        generate_pushid_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    # The key is pushid, value is bidprice
    pushid_bidprice_dict = dict()
    for i in range(thread_num):
        threads[i].join()
        temp_dict = threads[i].get_result()
        #logging.info("len of {0} temp_set is {1}".format(threads[i].getName(), len(temp_set)))
        pushid_bidprice_dict.update(temp_dict)

    logging.info("total bidres pushid num: {0}".format(len(pushid_bidprice_dict)))
    flush_pushid_bidprice_dict(pushid_bidprice_dict, pushid_bidprice_file)

    # This dict key is the host, value is a list, in which is the bid price
    host_bidprice_dict = dict()
    # This dict key is the adspace id, value is a list, in which is the bid price
    adspace_bidprice_dict = dict()
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if ((len(file_list) % FILES_PER_THREAD) != 0):
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(get_adspace_thread, (adid, pushid_bidprice_dict, file_list[i *
            FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD], "rtb_bid"),
            generate_pushid_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(get_adspace_thread, (adid, pushid_bidprice_dict, file_list[(thread_num - 1) *
        FILES_PER_THREAD: len(file_list)], "rtb_bid"),
        generate_pushid_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        temp_dict = threads[i].get_result()
        #logging.info("len of {0} temp_set is {1}".format(threads[i].getName(), len(temp_set)))
        #adspace_bidprice_dict.update(temp_dict)
        merge_adspace_bidprice_dict(adspace_bidprice_dict, temp_dict)

    logging.info("total adspace num: {0}".format(len(adspace_bidprice_dict)))
    flush_adspace_bidprice_dict(adspace_bidprice_dict, adspace_bidprice_file)


