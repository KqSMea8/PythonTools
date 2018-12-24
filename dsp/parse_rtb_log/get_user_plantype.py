#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-30 09:41:26

"""
This script parse the bidder log to calculate the ad type for every user
"""

from __future__ import print_function
import string
import sys
import os
import logging
import time
import esm
import hashlib
import base64

import threading

UA_MD5=dict()
UA_BASE64=dict()
BASE64_UA=dict()

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
        logging.info("starting %s at: %s" % (self.name, time.ctime()))
        self.res = self.func(*self.args)
        logging.info("finished %s at: %s" % (self.name, time.ctime()))

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
                if (len(result) == 0):
                    continue;
                files.append(os.path.join(parent, filename))
    else:
        if (len(index.query(dir_name)) != 0):
            files.append(dir_name)

    return files

def get_md5(ua):
    """
    This function get the md5 for the ua
    """
    global UA_MD5
    if ua in UA_MD5:
        return UA_MD5[ua]
    else:
        m = hashlib.md5()
        m.update(ua)
        md5value=m.hexdigest()
        UA_MD5[ua]=md5value
        return md5value

def get_base64(ua):
    """
    This function get the md5 for the ua
    """
    ua = ua.strip()
    global UA_BASE64
    if ua in UA_BASE64:
        return UA_BASE64[ua]
    else:
        ua_b64str = base64.b64encode(ua)
        ua_str = str(len(ua_b64str)) + ua_b64str
        b64value = ua_str[0:15]
        UA_BASE64[ua] = b64value
        #BASE64_UA[b64value] = ua
        return b64value


def generate_file(user_plantype_dict, file_name, filter_str):
    """
    generate the pushid from the file specified by file_name which ad id is
    equvalent to the adid
    the filter_str can be bid,bidres,rtb_creative,rtb_show,rtb_click now
    rtb_noAd and rtb_visit don't have pushid
    """
    if (None == user_plantype_dict or None == file_name or 0 == len(file_name)):
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
                if (0 == cmp(strs[0].strip(), filter_str) and len(strs) == 36 and 0 != len(strs[14]) and 0 != int(strs[13])):
                    #print("compare result of {0} and {1} is {2}".format(strs[0],
                    #    filter_str, cmp(strs[0], filter_str)))
                    #print("compare result {0} and {1} is {2}".format(strs[6],
                    #    adid, cmp(strs[6], adid)))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != rtb_show")
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    #print("key: {0}".format(key))
                    #strs[7] is pushid, strs[8] is ip
                    #print(len(strs))
                    key = strs[14] + "\1" + get_base64(strs[35])
                    user_plantype_dict.setdefault(key, None)
                    if user_plantype_dict[key] == None:
                        value={"10":0, "20":0, "30":0, "40":0, "100":0, "101":0}
                        value[strs[13]]+=1
                        user_plantype_dict[key]=value
                    else:
                        user_plantype_dict[key][strs[13]]+=1
                else:
                    #print("%s" % (strs[0]))
                    continue
    #logging.info("[generate_pushid_file]finish parse file: " + file_name)

def generate_thread(file_list, filter_str):
    """
    generate the pushid list
    """

    if (None == file_list or 0 == len(file_list)):
        return

    user_plantype_dict = dict()
    for file_name in file_list:
        generate_file(user_plantype_dict, file_name, filter_str)

    return user_plantype_dict
	
def print_pushid_ip_dict(pushid_ip_dict):
    for key in pushid_ip_dict.keys():
        print("{0}:{1}".format(key,pushid_ip_dict[key]))

def flush_all_dict(user_plantype_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for key in user_plantype_dict.keys():
            sub_dict = user_plantype_dict[key]
            outfd.write("user:%s\n" % (key))
            for sub_key in sub_dict.keys():
                outfd.write("%s:%d\t" % (sub_key, sub_dict[sub_key]))
            outfd.write("\n")

def flush_error_dict(user_plantype_dict, error_file):
    global BASE64_UA
    with open(error_file, mode="w") as outfd:
        for key in user_plantype_dict.keys():
            sub_dict = user_plantype_dict[key]
            if (sub_dict["10"] > 1 or sub_dict["20"] > 3 or sub_dict["30"]>2 or
                    sub_dict["40"] > 2 or sub_dict["100"] > 2 or sub_dict["101"] > 2):
                key_segs = key.split("\1")
                outfd.write("user:%s\n" % (key))
                for sub_key in sub_dict.keys():
                    outfd.write("%s:%d\t" % (sub_key, sub_dict[sub_key]))
                outfd.write("\n")

def flush_ua_base64(ua_file):
    global UA_BASE64
    with open(ua_file, mode="w") as outfd:
        for key in UA_BASE64:
            outfd.write("%s:%s\n" % (key, UA_BASE64[key]))

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
            for sub_key in add_dict[key].keys():
                orig_dict[key][sub_key]+= add_dict[key][sub_key]
        else:
            orig_dict[key]=add_dict[key]

FILES_PER_THREAD = 100

if __name__ == "__main__":
    init_logging()
    #file_name=raw_input("Please enter the file name: ");
    #print_file(file_name);
    """
    This dict's structure is as below:
    The key is user adsl, value is a dict,
    the structure of the value dict is as below:
    the key is ad plan type, value is times
    """
    user_plantype_dict = dict()
    out_dir = ""
    print(sys.argv)
    #first check the input argument
    if (len(sys.argv) < 3):
        print("Usage: " + os.path.basename(sys.argv[0]) + " <log_dir_name> <out_dir_name>")
        log_dir_name = raw_input("Please enter the directory name of the log file:\n")
        out_dir = raw_input("Please enter the out put directory:\n")
    else:
        log_dir_name = sys.argv[1]
        out_dir = sys.argv[2]

    filters = [""]
    if (len(sys.argv) > 3):
        filters = sys.argv[3:]
        logging.info("file name filter: {0}".format(filters))

    if out_dir[len(out_dir) - 1] != os.path.sep:
        out_dir = out_dir + os.path.sep

    if (not os.path.isdir(out_dir)):
        print("out directory is null!")
        out_dir = ""

    file_list = get_file_list(log_dir_name, filters)
    logging.info("number of log file is %d" % len(file_list))
    pushid_file = out_dir + "pushid.txt"
    error_file = out_dir + "error.txt"
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if ((len(file_list) % FILES_PER_THREAD) != 0):
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(generate_thread, (file_list[i *
            FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD], "rtb_creative"),
            generate_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(generate_thread, (file_list[(thread_num - 1) *
        FILES_PER_THREAD: len(file_list)], "rtb_creative"),
        generate_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        temp_dict = threads[i].get_result()
        logging.info("len of {0} temp_dict is {1}".format(threads[i].getName(),
            len(temp_dict.keys())))
        merge_dict(user_plantype_dict, temp_dict)

    logging.info("total user num: {0}".format(len(user_plantype_dict.keys())))
    flush_all_dict(user_plantype_dict, pushid_file)
    flush_error_dict(user_plantype_dict, error_file)

