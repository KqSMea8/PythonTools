#!/usr/bin/env python

"""
This script find the show failed url and show success url for specified adid
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""
from __future__ import print_function
import string
import sys
import os
import logging
import time
import esm
import getopt
from optparse import OptionParser

import threading

INDEX_MEANING_DICT = {22:"domain", 23:"url", 24:"adspace"}

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
                        filename="adx_get_url_count.log",
                        filemode="a")


def get_file_list(dir_name, filters_list):
    if (None == dir_name or 0 == len(dir_name)):
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    #print(len(filters_list))
    if (os.path.isdir(dir_name)):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                result = index.query(filename)
                #if (len(result) == 0):
                #    continue;
                if (len(filters_list) == 0) or (len(result) == len(filters_list)):
                    files.append(os.path.join(parent, filename))
    else:
        if (len(index.query(dir_name)) != 0):
            files.append(dir_name)

    return files


def get_url_file(ad_id, index, show_pushid_set, bidres_pushid_set, show_url_dict, unshow_url_dict, file_name):
    """
    get the url that show ad failed in file
    """
    if (None == show_pushid_set or None==bidres_pushid_set or None == file_name or 0 == len(file_name)):
        return

    #print("filter = " + string.join(id_filter))
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
                if (0 == cmp(strs[0], "rtb_bid") and (0 ==
                    cmp(strs[6], ad_id))):
                    if (strs[7] not in show_pushid_set) and (strs[7] in bidres_pushid_set):
                        if None == unshow_url_dict.get(strs[index]):
                            unshow_url_dict[strs[index]] = 1;
                        else:
                            unshow_url_dict[strs[index]] = unshow_url_dict.get(strs[index]) + 1;
                    elif (strs[7] in show_pushid_set):
                        if None == show_url_dict.get(strs[index]):
                            show_url_dict[strs[index]] = 1
                        else:
                            show_url_dict[strs[index]] = show_url_dict.get(strs[index]) + 1;

    logging.info("[get_url_file]finish parse file: " + file_name)


def get_url(ad_id, index, show_pushid_set, bidres_pushid_set, show_url_dict, unshow_url_dict, file_list):
    """
    get the url that show ad failed in directory
    """
    if (None == show_pushid_set or None==bidres_pushid_set or None == file_list or 0 == len(file_list)):
        return

    for file_name in file_list:
        get_url_file(ad_id, index, show_pushid_set, bidres_pushid_set, show_url_dict, unshow_url_dict, file_name)


def generate_pushid_file(adid, bidres_pushid_set, show_pushid_set, file_name):
    """
    generate the pushid from the file specified by file_name which ad id is
    equvalent to the adid
    """
    if (None == bidres_pushid_set or None == show_pushid_set or None == file_name or 0 == len(file_name)):
        return

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
                if (0 == cmp(strs[0], "rtb_bidres") and 0 == cmp(strs[6], adid)):
                    if (not strs[7] in bidres_pushid_set):
                        bidres_pushid_set.add(strs[7])
                elif (0 == cmp(strs[0], "rtb_show") and 0 == cmp(strs[6], adid)):
                    if (not strs[7] in show_pushid_set):
                        show_pushid_set.add(strs[7])
    logging.info("[generate_pushid_file]finish parse file: " + file_name)


def generate_pushid_thread(ad_id, file_list):
    """
    generate the pushid list
    """

    if (None == file_list or 0 == len(file_list)):
        return

    bidres_pushid_set = set()
    show_pushid_set = set()
    for file_name in file_list:
        generate_pushid_file(ad_id, bidres_pushid_set, show_pushid_set, file_name)

    return bidres_pushid_set, show_pushid_set


def print_dict(unshow_url_dict):
    for key in unshow_url_dict.keys():
        print('{0},{1}'.format(key, unshow_url_dict[key]))


def flush_dict(unshow_url_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for key in unshow_url_dict.keys():
            print('{0},{1}'.format(unshow_url_dict[key], key), file=outfd)


def print_pushid_set(pushid_list):
    for pushid in pushid_list:
        print("{0}".format(pushid))


def flush_pushid_set(pushid_list, file_name):
    with open(file_name, mode="w") as outfd:
        for pushid in pushid_list:
            print("{0}".format(pushid), file=outfd)


FILES_PER_THREAD = 2

if __name__ == "__main__":
    init_logging()
    """
    This dict's structure is as below:
    The key is pushid, value is tuple, the tuple contains access time and url
    """
    out_dir = ""
    print(sys.argv)

    parser = OptionParser()
    parser.add_option("-l", "--log-dir", dest="logdir", help="The directory name of the log file")
    parser.add_option("-o", "--out-dir", dest="outdir", help="The directory name of the out put directory")
    parser.add_option("-a", "--adid", dest="adid", help="The ad id to statistic")
    help_str = str()
    keys = INDEX_MEANING_DICT.keys()
    keys.sort()
    for key in keys:
        help_str += "%d:%s \n" % (key, INDEX_MEANING_DICT[key])
    parser.add_option("-I", "--index", dest="index", type=int, help="The index of the segements want to statistics, the value should one of the followrs: \n%s" % (help_str))
    parser.add_option("-f", "--filters", dest="filters", action="append", help="The filter string of the file name, this option could be specified several times")

    options,args = parser.parse_args()
    log_dir_name = options.logdir
    adid = options.adid
    out_dir = options.outdir
    index = options.index
    filters = list()
    if (options.filters != None):
        filters = options.filters
        print(filters)
    if (log_dir_name == None or adid == None or out_dir == None or index == None):
        parser.print_help()
        sys.exit(0)
    #if (len(sys.argv) > 5):
    #    filters = sys.argv[5:]
    #    logging.info("file name filter: {0}".format(filters))

    if out_dir[len(out_dir) - 1] != os.path.sep:
        out_dir = out_dir + os.path.sep

    if (os.path.exists(out_dir)):
        if os.path.isfile(out_dir):
            print("out directory is exist and is a file")
            sys.exit(-1)
    else:
        print("out directory is not exist, create now!")
        os.makedirs(out_dir)

    file_list = get_file_list(log_dir_name, filters)
    logging.info("number of log file is %d" % len(file_list))
    out_show_file = out_dir + "show_{0}_count.txt".format(INDEX_MEANING_DICT[int(index)]);
    out_unshow_file = out_dir + "unshow_{0}_count.txt".format(INDEX_MEANING_DICT[int(index)]);
    out_pushid_file = out_dir + "show_pushid.txt";

    bidres_pushid_set = set ()
    show_pushid_set = set()
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if ((len(file_list) % FILES_PER_THREAD) != 0):
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(generate_pushid_thread, (adid, file_list[i *
            FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD]),
            generate_pushid_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(generate_pushid_thread, (adid, file_list[(thread_num - 1) *
        FILES_PER_THREAD: len(file_list)]),
        generate_pushid_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        temp_bidres_set, temp_show_set = threads[i].get_result()
        logging.info("len of {0} temp_bidres_len is {1}, temp_show_len is {2}".format(threads[i].getName(),
            len(temp_bidres_set), len(temp_show_set)))
        bidres_pushid_set.update(temp_bidres_set)
        show_pushid_set.update(temp_show_set)

    logging.info("total show pushid num: {0}".format(len(show_pushid_set)))
    logging.info("total bidres pushid num: {0}".format(len(bidres_pushid_set)))

    flush_pushid_set(show_pushid_set, out_pushid_file)

    show_dict = dict()
    unshow_dict = dict()
    index = int(index)
    get_url(adid, index, show_pushid_set, bidres_pushid_set, show_dict, unshow_dict, file_list)
    flush_dict(show_dict, out_show_file)
    flush_dict(unshow_dict, out_unshow_file)

