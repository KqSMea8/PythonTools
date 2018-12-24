#!/usr/bin/env python

"""
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""
from __future__ import print_function
import string
import sys
import os

def get_log_file_name(log, id=""):
    month = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6',
             'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10','Nov':'11','Dec':'12'}
    logs_new = string.split(log, sep=" ");
    strs = string.split(logs_new[0], sep="-");
    return strs[1] + "_" + strs[2] + id + ".csv"

def is_key_in_list(key, key_list):
    for str in key_list:
        if (0 == cmp(key, str)):
            return True

    return False

def parse_bidder_log_file(ad_dict, base_id, id_site_dict, file_name, id_filter):
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
                    log_file_name = get_log_file_name(strs[4])
                    if (None == ad_dict.get(log_file_name)):
                        ad_dict[log_file_name] = dict()
                    host = id_site_dict.get(strs[7])
                    if (None == host or 0 == len(host)):
                        #print("can't find host for pushid " + strs[7])
                        continue
                    aid_host = strs[6] + "_" + host
                    if ad_dict[log_file_name].get(aid_host) == None:
                        ad_dict[log_file_name][aid_host] = [0, 0, 0, 0]
                    index = show_click_id[strs[0]]
                    ad_dict[log_file_name][aid_host][int(index) + base_id] += 1
                    #print(strs[4] + "<>" + strs[6] + "<>" + strs[7])
    print("[parse_bidder_log_file]finish parse file: " + file_name)

def parse_bidder_log(ad_dict, base_id, id_site_dict, dir_name):
    id_filter = ["rtb_show", "rtb_click"]
    if (None == ad_dict or None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    parse_bidder_log(ad_dict, base_id, id_site_dict, os.path.join(parent,dirname))

            for filename in filenames:                      #display file information
                parse_bidder_log_file(ad_dict, base_id, id_site_dict, os.path.join(parent,filename), id_filter)
    else:
        parse_bidder_log_file(ad_dict, base_id, id_site_dict, dir_name, id_filter)

def generate_pushid_site_file(id_site_dict, file_name, id_filter=""):
    if (None == id_site_dict or None == file_name or 0 == len(file_name)):
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
                    if (None == id_site_dict.get(strs[7]) or
                        0 != cmp(id_site_dict.get(strs[7]), strs[22])):
                        id_site_dict[strs[7]] = strs[22]
    print("[generate_pushid_site_file]finish parse file: " + file_name)
"""
generate the pushid and the host map
"""
def generate_pushid_site(id_site_dict, dir_name):
    if (None == id_site_dict or None == dir_name or 0 == len(dir_name)):
        return

    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            #for dirname in dirnames:                       #display directory information
            #    generate_pushid_site(id_site_dict, os.path.join(parent,dirname))
            
            for filename in filenames:                      #display file information
                generate_pushid_site_file(id_site_dict, os.path.join(parent,filename), "rtb_creative")
    else:
        generate_pushid_site_file(id_site_dict, dir_name, "rtb_creative")
        
def print_total_dict(total_dict):
    for key in total_dict.keys():
        id_site_dict = total_dict[key]
        for id_site in id_site_dict.keys():
            strs = string.split(id_site, "_")
            print('%s,%s,%s,%s,%s' % (key, strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]))

def flush_total_dict(total_dict):
    for key in total_dict.keys():
        file_name = out_dir + key
        with open(file_name, mode="w") as logfd:
            id_site_dict = total_dict[key]
            for id_site in id_site_dict.keys():
                strs = string.split(id_site, "_")
                print('%s,%s,%s,%s' % (strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]), file=logfd)

def print_id_site_dict(id_site_dict):
    for key in id_site_dict.keys():
        print('%s,%s' % (key, id_site_dict[key]))

#file_name=raw_input("Please enter the file name: ");
#print_file(file_name);
"""
This dict's structure is as below:
the first dimension is log_file_name, the value is a dict too;
the second dimension is aid_host, the value is a list, in which the first value is the show times,
the second is the click times
"""
total_dict = dict()
id_site_dict = dict()
out_dir = ""
base_id_map = {'zhejiang':'0', 'jiangsu':'2'}
show_click_id = {'rtb_show':'0', 'rtb_click':'1'}


print(sys.argv)
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

generate_pushid_site(id_site_dict, zj_dir_name)
generate_pushid_site(id_site_dict, js_dir_name)
print_id_site_dict(id_site_dict)
#parse_click_log(total_dict)
#parse_show_log(total_dict)
parse_bidder_log(total_dict, 0, id_site_dict, zj_dir_name)
parse_bidder_log(total_dict, 2, id_site_dict, js_dir_name)
print_total_dict(total_dict)
flush_total_dict(total_dict)

