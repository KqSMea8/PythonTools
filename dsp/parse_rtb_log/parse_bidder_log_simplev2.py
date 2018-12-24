#!/usr/bin/env python
from __future__ import print_function

"""
This version of parse bidder log can analysis one day per time, consider the show times and the create times is almost equivalent
Algorithm:
first: read all the click times into the memory
second: parse all log files to search the create times, and convert the pushid of the click record to host
"""

"""
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""

import string
import sys
import os
import time

def print_cur_time(prefix="current time is "):
    ISOTIMEFORMAT='%Y-%m-%d %X'
    time_str = time.strftime(ISOTIMEFORMAT, time.localtime())
    print(prefix + time_str)

def get_log_file_name(log_time, id=""):
    """
    According to the log time, generate the log file name
    For example, if log_time is 2016-03-16 19:10:59, then the return file name
    if 03_16.csv
    """
    month = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6',
             'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10','Nov':'11','Dec':'12'}
    logs_new = string.split(log_time, sep=" ");
    strs = string.split(logs_new[0], sep="-");
    return strs[1] + "_" + strs[2] + id + ".csv"

def is_key_in_list(key, key_list):
    for str in key_list:
        if (0 == cmp(key, str)):
            return True

    return False

def check_pushid_click(pushid, click_dict):
    for click_pushid in click_dict.keys():
        if (0 == cmp(click_pushid, pushid)):
            return True

    return False

def generate_click_map_file(click_dict, file_name, id_filter):
    if (None == click_dict or None == file_name or 0 == len(file_name) or None == id_filter):
        return;

    #filter *.tar.gz
    if (-1 != string.find(file_name ,".tar.gz")):
        return
    
    if (not os.path.isfile(file_name)):
        print(file_name + " is not a file!")
    else:
        if (not string.find(file_name, "rtb_log_crit_", 0, len("rtb_log_crit_"))):
            print(file_name + " is not rtb_log_crit log file")
            return;
        with open(file_name) as fd:
            for line in fd:
                strs = string.split(line, sep="\1")
                strs[0] = string.strip(strs[0])
                if (0 != len(id_filter) and 0 != cmp(strs[0], id_filter)):
                    #print("compare result is %d" % cmp(strs[0], id_filter))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != " + id_filter)
                    continue
                else:
                    global log_file_name
                    if (0 == len(log_file_name)):
                        log_file_name = get_log_file_name(strs[4])
                    if click_dict.get(strs[7]) == None:
                        click_dict[strs[7]] = strs[6]
    #print("[generate_click_map_file]finish parse file: " + file_name)

def generate_click_map(click_dict, dir_name):
    if (None == click_dict or None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                         # parse each file
                generate_click_map_file(click_dict, os.path.join(parent, filename), "rtb_click")
    else:
        generate_click_map_file(click_dict, dir_name, "rtb_click")

def parse_create_pushid_site_file(click_dict, total_dict, file_name, base_id, id_filter=""):
    if (None == file_name or 0 == len(file_name) or None == click_dict or None == total_dict):
        return;

    #filter *.tar.gz
    if (-1 != string.find(file_name ,".tar.gz")):
        return
    
    if (not os.path.isfile(file_name)):
        print(file_name + " is not a file!")
    else:
        if (not string.find(file_name, "rtb_log_crit_", 0, len("rtb_log_crit_"))):
            print(file_name + " is not rtb_log_crit log file")
            return;
        with open(file_name) as fd:
            for line in fd:
                strs = string.split(line, sep="\1")
                strs[0] = string.strip(strs[0])
                if (0 != len(id_filter) and 0 != cmp(strs[0],id_filter)):
                    #print("compare result is %d" % cmp(strs[0], id_filter))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != " + id_filter)
                    continue
                else:
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7] + "<>" + strs[22])
                    aid_site = strs[6] + "_" + strs[22]
                    if (total_dict.get(aid_site) == None):
                        total_dict[aid_site] = [0,0,0,0]
                    if (True == check_pushid_click(strs[7], click_dict)):
                        click_index = show_click_id["rtb_click"]
                        total_dict[aid_site][int(click_index) + base_id] += 1
                    show_index = show_click_id["rtb_show"]
                    total_dict[aid_site][int(show_index) + base_id] += 1
    print("[parse_create_pushid_site_file]finish parse file: " + file_name)
"""
generate the pushid and the host map
"""
def parse_create_pushid_site(click_dict, total_dict, dir_name, base_id):
    if (None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    generate_pushid_site(id_site_dict, os.path.join(parent,dirname))
            
            for filename in filenames:                      #display file information
                parse_create_pushid_site_file(click_dict, total_dict, os.path.join(parent,filename), base_id, "rtb_creative")
    else:
        parse_create_pushid_site_file(click_dict, total_dict, dir_name, base_id, "rtb_creative")
        
def print_total_dict(total_dict):
    for aid_site in total_dict.keys():
        strs = string.split(aid_site, "_")
        print('%s,%s' % (strs[0], strs[1]))
        for value in total_dict[aid_site]:
            print(',%d' % value, end = "")
        print

def flush_total_dict(total_dict):
    global log_file_name
    file_name = out_dir + log_file_name
    with open(file_name, mode="w") as logfd:
        for aid_site in total_dict.keys():
            strs = string.split(aid_site, "_")
            print('%s,%s' % (strs[0], strs[1]), end = "", file=logfd)
            for value in total_dict[aid_site]:
                print(',%d' % value, end = "", file=logfd)
            print("", file=logfd)
            #print('%s,%s,%s,%s' % (strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]), file=logfd)

def print_click_dict(click_dict):
    for pushid in click_dict.keys():
        print("click push id: %s, aid: %s" % (pushid, click_dict.get(pushid)))

"""
This dict's structure is as below:
the first dimension is aid_pushid, the value is a list, in which the first value is the show times,
the second is the click times
"""
total_dict = dict()
click_dict = dict()
out_dir = ""
global log_file_name
log_file_name = ""
#base_id_map = {'zhejiang':'0', 'jiangsu':'2'}
show_click_id = {'rtb_show':'0', 'rtb_click':'1'}

#first check the input argument
if (4 != len(sys.argv)):
    print("Usage: " + os.path.basename(sys.argv[0]) + " <zj_log_dir_name> <js_log_dir_name> <out_dir_name>")
    zj_dir_name = raw_input("Please enter the directory name of the zhejiang log file:\n")
    js_dir_name = raw_input("Please enter the directory name of the jiangsu log file:\n")
    out_dir = raw_input("Please enter the out put directory:\n")
else:
    zj_dir_name = sys.argv[1]
    js_dir_name = sys.argv[2]
    out_dir = sys.argv[3]

if out_dir[len(out_dir) - 1] != os.path.sep:
    out_dir = out_dir + os.path.sep

if (not os.path.isdir(out_dir)):
    print("out directory is null!")
    out_dir = ""

print_cur_time()
generate_click_map(click_dict, zj_dir_name)
print_cur_time("finish generate_click_map zhejiang is ")
generate_click_map(click_dict, js_dir_name)
print_cur_time("finish generate_click_map jiangsu is ")
print_click_dict(click_dict)
parse_create_pushid_site(click_dict, total_dict, zj_dir_name, 0)
print_cur_time("finish parse_create_pushid_site zhejiang is ")
parse_create_pushid_site(click_dict, total_dict, js_dir_name, 2)
print_cur_time("finish parse_create_pushid_site jiangsu is ")
#print_total_dict(total_dict)
flush_total_dict(total_dict)
print_cur_time("end time is ")

