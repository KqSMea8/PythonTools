#!/usr/bin/env python

"""
This script find the show failed url for specified adid
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""
from __future__ import print_function
import string
import sys
import os
import logging

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
    while (low <= high):
        mid = (low + high) / 2
        cmp_value = cmp(key, data[mid])
        if (cmp_value < 0):
            high = mid - 1
        elif (cmp_value > 0):
            low = mid + 1
        else:
            return mid

    return -1

def get_log_file_name(log, id=""):
    month = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6',
             'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10','Nov':'11','Dec':'12'}
    logs_new = string.split(log, sep=" ");
    strs = string.split(logs_new[0], sep="-");
    return strs[1] + "_" + strs[2] + id + ".csv"

def is_key_in_list(key, key_list):
    if (-1 != binary_search(key, key_list)):
            return True

    return False

def get_unshow_url_file(ad_id, show_pushid_list, unshow_url_dict, file_name):
    """
    get the url that show ad failed in file
    """
    if (None == show_pushid_list or None == file_name or 0 == len(file_name)):
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
                if (0 == cmp(strs[0], "rtb_creative") and (0 ==
                        cmp(strs[6], ad_id)) and (True != is_key_in_list(strs[7], show_pushid_list))):
                    #unshow_url_dict[strs[7]] = (strs[4], strs[22], strs[23])
                    if None == unshow_url_dict.get(strs[23]):
                        unshow_url_dict[strs[23]] = 1;
                    else:
                        unshow_url_dict[strs[23]] = unshow_url_dict.get(strs[23]) + 1;
    logging.info("[get_unshow_url_file]finish parse file: " + file_name)

def get_unshow_url(ad_id, show_pushid_list, unshow_url_dict, dir_name):
    """
    get the url that show ad failed in directory
    """
    if (None == show_pushid_list or None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    parse_bidder_log(ad_dict, base_id, id_site_dict, os.path.join(parent,dirname))

            for filename in filenames:                      #display file information
                get_unshow_url_file(ad_id, show_pushid_list, unshow_url_dict, os.path.join(parent,filename))
    else:
        get_unshow_url_file(ad_id, show_pushid_list, unshow_url_dict, dir_name)

def generate_show_pushid_file(adid, show_pushid_list, file_name):
    if (None == show_pushid_list or None == file_name or 0 == len(file_name)):
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
                if (0 != cmp(strs[0], "rtb_show") or 0 != cmp(strs[6], adid)):
                    #print("compare result of {0} and {1} is {2}".format(strs[0],
                    #    "rtb_show", cmp(strs[0], "rtb_show")))
                    #print("compare result {0} and {1} is {2}".format(strs[6],
                    #    adid, cmp(strs[6], adid)))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != rtb_show")
                    continue
                else:
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    if (not strs[7] in show_pushid_list):
                        show_pushid_list.append(strs[7])
    logging.info("[generate_show_pushid_file]finish parse file: " + file_name)

def generate_show_pushid(ad_id, show_pushid_list, log_dir_name):
    """
    generate the pushid and the host map
    """

    if (None == show_pushid_list or None == log_dir_name or 0 == len(log_dir_name)):
        return

    if os.path.isdir(log_dir_name):
        for parent, dirnames, filenames in os.walk(log_dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    generate_pushid_site(id_site_dict, os.path.join(parent,dirname))
 
            for filename in filenames:                      #display file information
                generate_show_pushid_file(ad_id, show_pushid_list, os.path.join(parent,filename))
    else:
        generate_show_pushid_file(ad_id, show_pushid_list, log_dir_name)

def print_unshowurl_dict(unshow_url_dict):
    for key in unshow_url_dict.keys():
        print('{0},{1}'.format(key, unshow_url_dict[key]))

def flush_unshowurl_dict(unshow_url_dict, file_name):
    with open(file_name, mode="w") as outfd:
        for key in unshow_url_dict.keys():
            print('{0},{1}'.format(key, unshow_url_dict[key]), file=outfd)

def print_pushid_list(pushid_list):
    for pushid in pushid_list:
        print("{0}".format(pushid))

def flush_pushid_list(pushid_list, file_name):
    with open(file_name, mode="w") as outfd:
        for pushid in pushid_list:
            print("{0}".format(pushid), file=outfd)


if __name__ == "__main__":
    init_logging()
    #file_name=raw_input("Please enter the file name: ");
    #print_file(file_name);
    """
    This dict's structure is as below:
    The key is adid, value is pushid
    """
    show_pushid_list = list()
    """
    This dict's structure is as below:
    The key is pushid, value is tuple, the tuple contains access time and url
    """
    unshow_url_dict = dict()
    out_dir = ""

    print(sys.argv)
    #first check the input argument
    if (4 != len(sys.argv)):
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

    out_file = out_dir + "unshow_url_count.txt";
    out_pushid_file = out_dir + "unshow_pushid.txt";
    logging.info("start generate_show_pushid")
    generate_show_pushid(adid, show_pushid_list, log_dir_name)
    logging.info("start sort pushid list")
    show_pushid_list.sort()
    logging.info("start print_show_pushid")
    #print_pushid_list(show_pushid_list)
    logging.info("start flush pushid list")
    flush_pushid_list(show_pushid_list, out_pushid_file)
    logging.info("start get unshow url")
    get_unshow_url(adid, show_pushid_list, unshow_url_dict, log_dir_name)
    #print_unshowurl_dict(unshow_url_dict)
    logging.info("start flush unshow url")
    flush_unshowurl_dict(unshow_url_dict, out_file)
    logging.info("finish all")

