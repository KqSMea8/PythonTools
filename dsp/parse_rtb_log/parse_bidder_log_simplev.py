#!/usr/bin/env python
from __future__ import print_function

"""
This version of parse bidder log can analysis one day per time
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

def clear_env():
    for fd in db_file_fd:
        if (None != fd):
            close(fd)

def get_log_file_name(log_time, id=""):
    month = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6',
             'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10','Nov':'11','Dec':'12'}
    logs_new = string.split(log_time, sep=" ");
    strs = string.split(logs_new[0], sep="-");
    return strs[1] + "_" + strs[2] + id + ".csv"

def get_db_file_name(log_time, id=""):
    logs_new = string.split(log_time, sep=" ");
    strs = string.split(logs_new[0], sep="-");
    return strs[1] + "_" + strs[2] + id + ".db"

def get_host_from_db(pushid, db_file):
    if (None == db_file or None == pushid):
        return None

    for line in db_file:
        strs = string.split(line, "\1")
        if (0 == cmp(strs[0], pushid)):
            return strs[1]

    return None

def write_host_to_db(pushid, host, db_file):
    if (None == db_file or None == pushid or None == host):
        return 0;

    print("%s\1%s" % (pushid, host), file=db_file)

def is_key_in_list(key, key_list):
    for str in key_list:
        if (0 == cmp(key, str)):
            return True

    return False

def parse_bidder_log_file(ad_dict, base_id, file_name, id_filter):
    if (None == ad_dict or None == file_name or 0 == len(file_name) or None == id_filter):
        return;

    #print("filter = " + string.join(id_filter))
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
                if (0 != len(id_filter) and True != is_key_in_list(strs[0], id_filter)):
                    #print("compare result is %d" % cmp(strs[0], id_filter))
                    #print("find result is %d" % string.find(strs[0], id_filter))
                    #print(strs[0] + " != " + id_filter)
                    continue
                else:
                    if (0 == len(log_file_name)):
                        log_file_name = get_log_file_name(strs[4])

                    aid_pushid = strs[6] + "_" + strs[7]
                    if ad_dict.get(aid_pushid) == None:
                        ad_dict[aid_pushid] = [0, 0, 0, 0]
                    index = show_click_id[strs[0]]
                    ad_dict[aid_pushid][int(index) + base_id] += 1
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7])
    print("[parse_bidder_log_file]finish parse file: " + file_name)

def parse_bidder_log(ad_dict, base_id, dir_name):
    id_filter = ["rtb_show", "rtb_click"]
    if (None == ad_dict or None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                         # parse each file
                parse_bidder_log_file(ad_dict, base_id, os.path.join(parent, filename), id_filter)
    else:
        parse_bidder_log_file(ad_dict, base_id, dir_name, id_filter)

def generate_pushid_site_file(file_name, id_filter=""):
    if (None == file_name or 0 == len(file_name)):
        return;

    #print("filter = " + id_filter)
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
                    if (None == db_file_fd[1]):
                        db_file_name = get_db_file_name(strs[4])
                        fd = open(out_dir + db_file_name, mode="w")
                        if (None == fd):
                            print("open write file failed")
                            return;
                        print("write fd = %d" % fd.fileno())
                        db_file_fd[1] = fd
                    if (None == db_file_fd[0]):
                        db_file_name = get_db_file_name(strs[4])
                        fd = open(out_dir + db_file_name, mode="r")
                        if (None == fd):
                            print("open read file failed")
                            return;
                        print("read fd = %d" % fd.fileno())
                        db_file_fd[0] = fd
                    if (None == get_host_from_db(strs[7], db_file_fd[0])):
                        write_host_to_db(strs[7], strs[22], db_file_fd[1])
                        file.flush(db_file_fd[1])
                        #id_site_dict[strs[7]] = strs[22]
    print("[generate_pushid_site_file]finish parse file: " + file_name)
"""
generate the pushid and the host map
"""
def generate_pushid_site(dir_name):
    if (None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    generate_pushid_site(id_site_dict, os.path.join(parent,dirname))
            
            for filename in filenames:                      #display file information
                generate_pushid_site_file(os.path.join(parent,filename), "rtb_creative")
    else:
        generate_pushid_site_file(dir_name, "rtb_creative")
        
def print_total_dict(total_dict):
    for aid_pushid in total_dict.keys():
        strs = string.split(aid_pushid, "_")
        host = get_host_from_db(strs[1], db_file_fd[0])
        #print('%s,%s,%s,%s' % (strs[0], host, total_dict[aid_pushid][0], total_dict[aid_pushid][1]))
        print('%s,%s' % (strs[0], host), end = "")
        for value in total_dict[aid_pushid]:
            print(',%s' % value, end = "")
        print

def flush_total_dict(total_dict):
    file_name = out_dir + log_file_name
    with open(file_name, mode="w") as logfd:
        for aid_pushid in total_dict.keys():
            strs = string.split(aid_pushid, "_")
            host = get_host_from_db(strs[1], db_file_fd[0])
            print('%s,%s,%s,%s' % (strs[0], host, id_site_dict[id_site][0], id_site_dict[id_site][1]), file=logfd)

def print_id_site_dict():
    for line in db_file_fd[0]:
        print(line)

"""
This dict's structure is as below:
the first dimension is aid_pushid, the value is a list, in which the first value is the show times,
the second is the click times
"""
total_dict = dict()
out_dir = ""
log_file_name = ""
db_file_fd = [None, None]
base_id_map = {'zhejiang':'0', 'jiangsu':'2'}
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
generate_pushid_site(zj_dir_name)
generate_pushid_site(js_dir_name)
print_id_site_dict()
print_cur_time("end time is ")
#parse_click_log(total_dict)
#parse_show_log(total_dict)
#parse_bidder_log(total_dict, 0, id_site_dict, zj_dir_name)
#parse_bidder_log(total_dict, 2, id_site_dict, js_dir_name)
#print_total_dict(total_dict)
#flush_total_dict(total_dict)
clear_env()

