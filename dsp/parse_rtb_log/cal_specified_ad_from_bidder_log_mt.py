#!/usr/bin/env python
from __future__ import print_function

"""
这个脚本用于解析bidder日志，生成浙江和江苏的同一个广告在一天中的展示和点击次数
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
import threading

class MyThread(threading.Thread):
    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        print("starting %s at: %s" % (self.name, time.ctime()))
        self.res = self.func(*self.args)
        print("finished %s at: %s" % (self.name, time.ctime()))

    def getResult(self):
        return self.res

def print_cur_time(prefix="current time is "):
    ISOTIMEFORMAT='%Y-%m-%d %X'
    time_str = time.strftime(ISOTIMEFORMAT, time.localtime())
    print(prefix + time_str)

def get_log_file_name(log_time, id=""):
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

def generate_click_map_file_thread(files, aid, id_filter):
    if (None == files or 0 == len(files) or None == aid or 0 == len(aid) or None == id_filter):
        return None;

    count = 0
    click_dict = dict()
    for file_name in files:
        #filter *.tar.gz
        if (-1 != string.find(file_name ,".tar.gz")):
            continue
        
        if (not os.path.isfile(file_name)):
            print(file_name + " is not a file!")
        else:
            if (not string.find(file_name, "rtb_log_crit_", 0, len("rtb_log_crit_"))):
                print(file_name + " is not rtb_log_crit log file")
                continue;
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
                        if (0 != cmp(strs[6], aid)):
                            continue
                        
                        if click_dict.get(strs[7]) == None:
                            click_dict[strs[7]] = strs[6]
                            count += 1
                        else:
                            print(strs[7] + " already exists")
        #print("[generate_click_map_file]finish parse file: " + file_name)
    print("name is %s, count = %d" % (threading.currentThread().getName(), count))
    return click_dict

def parse_create_pushid_site_file_thread(click_dict, files, aid, id_filter=""):
    if (None == click_dict or None == aid or 0 == len(aid)):
        return None;

    total_dict = dict()
    for file_name in files:
        #filter *.tar.gz
        if (-1 != string.find(file_name ,".tar.gz")):
            continue
        
        if (not os.path.isfile(file_name)):
            print(file_name + " is not a file!")
        else:
            if (not string.find(file_name, "rtb_log_crit_", 0, len("rtb_log_crit_"))):
                print(file_name + " is not rtb_log_crit log file")
                continue;
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
                        if (0 != cmp(strs[6], aid)):
                            continue;
                        aid_site = strs[22]
                        if (total_dict.get(aid_site) == None):
                            total_dict[aid_site] = [0,0]
                        if (True == check_pushid_click(strs[7], click_dict)):
                            click_index = show_click_id["rtb_click"]
                            total_dict[aid_site][int(click_index)] += 1
                        show_index = show_click_id["rtb_show"]
                        total_dict[aid_site][int(show_index)] += 1
        #print("[parse_create_pushid_site_file]finish parse file: " + file_name)
    return total_dict

def get_file_list(dir_name):
    if (None == dir_name or 0 == len(dir_name)):
        return None

    files = []
    if (os.path.isdir(dir_name)):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                files.append(os.path.join(parent,filename))
    else:
        files.append(dir_name)

    return files
        
def print_total_dict(total_dict):
    for aid_site in total_dict.keys():
        strs = string.split(aid_site, "_")
        print('%s,%s' % (strs[0], strs[1]))
        for value in total_dict[aid_site]:
            print(',%d' % value, end = "")
        print

def flush_total_dict(total_dict, file_name):
    with open(file_name, mode="w") as logfd:
        for host in total_dict.keys():
            print('%s' % host, end = "", file=logfd)
            for value in total_dict[host]:
                print(',%d' % value, end = "", file=logfd)
            print("", file=logfd)
            #print('%s,%s,%s,%s' % (strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]), file=logfd)

def print_click_dict(click_dict):
    file_name = "D:\MySource\PythonSource\output\click_dict.txt"
    with open(file_name, mode = "w") as clickfd:
        for pushid in click_dict.keys():
            print("click push id: %s, aid: %s" % (pushid, click_dict.get(pushid)), file=clickfd)

def print_file_list(files):
    for file_name in files:
        print(file_name)

def merge_total_dict(new_dict, total_dict):
    for new_key in new_dict.keys():
        found = False
        for old_key in total_dict.keys():
            if (0 == cmp(new_key, old_key)):
                total_dict[old_key][0] += new_dict[new_key][0]
                total_dict[old_key][1] += new_dict[new_key][1]
                found = True
                break
        if (True != found):
            total_dict[new_key] = [new_dict[new_key][0], new_dict[new_key][1]]

def merge_zj_js_total_dict(zj_total_dict, js_total_dict):
    total_dict = dict()
    for js_key in js_total_dict:
        total_dict[js_key] = [0, 0, js_total_dict[js_key][0], js_total_dict[js_key][1]]
        
    for zj_key in zj_total_dict.keys():
        if zj_key in js_total_dict:
            total_dict[zj_key][0] += zj_total_dict[zj_key][0]
            total_dict[zj_key][1] += zj_total_dict[zj_key][1]
        else:
            total_dict[zj_key] = [zj_total_dict[zj_key][0], zj_total_dict[zj_key][1], 0, 0]

    return total_dict
            
#base_id_map = {'zhejiang':'0', 'jiangsu':'2'}
show_click_id = {'rtb_click':'0', 'rtb_show':'1'}
CLICK_FILES_PER_THREAD = 1000
SHOW_FILES_PER_THREAD = 100

def main():
    zj_total_dict = dict()
    js_total_dict = dict()
    zj_click_dict = dict()
    js_click_dict = dict()
    out_dir = ""

    #first check the input argument
    if (6 != len(sys.argv)):
        print("Usage: " + os.path.basename(sys.argv[0]) + " <zj_log_dir_name> <js_log_dir_name> <zj_aid> <js_aid> <out_dir_name>")
        zj_dir_name = raw_input("Please enter the directory name of the zhejiang log file:\n")
        js_dir_name = raw_input("Please enter the directory name of the jiangsu log file:\n")
        zj_aid = raw_input("Please enter the aid of the zhejiang ad:\n")
        js_aid = raw_input("Please enter the aid of the jiangsu ad:\n")
        log_file_name = raw_input("Please enter the out put file path:\n")
    else:
        zj_dir_name = sys.argv[1]
        js_dir_name = sys.argv[2]
        zj_aid = sys.argv[3]
        js_aid = sys.argv[4]
        log_file_name = sys.argv[5]

    print_cur_time()
    zj_files = get_file_list(zj_dir_name)
    print("file number of zhejiang is %d" % len(zj_files))
    print_cur_time("finish get_file_list zhejiang is ")
    js_files = get_file_list(js_dir_name)
    print("file number of jiangsu is %d" % len(js_files))
    print_cur_time("finish get_file_list jiangsu is ")

    js_click_dict = generate_click_map_file_thread(js_files, js_aid, "rtb_click")
    print_cur_time("finish generate_click_map jiangsu is ")
    print(len(js_click_dict.keys()))
    print_click_dict(js_click_dict)
    
    click_threads = []
    thread_num = len(zj_files) / CLICK_FILES_PER_THREAD + 1
    print("click threads num: %d" % thread_num)
    for i in range(thread_num - 1):
        t = MyThread(generate_click_map_file_thread,
                     (zj_files[i * CLICK_FILES_PER_THREAD: (i + 1) * CLICK_FILES_PER_THREAD], zj_aid, "rtb_click"),
                     generate_click_map_file_thread.__name__ + "_" + str(i))
        click_threads.append(t)
    t = MyThread(generate_click_map_file_thread,
                 (zj_files[thread_num - 1 * CLICK_FILES_PER_THREAD: len(zj_files)], zj_aid, "rtb_click"),
                 generate_click_map_file_thread.__name__ + "_" + str(thread_num - 1))
    click_threads.append(t)
    
    for i in range(thread_num):
        click_threads[i].start()

    for i in range(thread_num):
        click_threads[i].join()
        temp_dict = click_threads[i].get_result()
        print("len of %s temp_dict is %d" % (click_threads[i].getName(), len(temp_dict.keys())))
        zj_click_dict.update(temp_dict)

    print(len(zj_click_dict.keys()))
    print_click_dict(zj_click_dict)
    #zj_click_dict = generate_click_map_file_thread(zj_files, zj_aid, "rtb_click")
    print_cur_time("finish generate_click_map zhejiang is ")

    js_total_dict = parse_create_pushid_site_file_thread(js_click_dict, js_files, js_aid, "rtb_creative")
    print("len of jiangsu total dict is %d" % (len(js_total_dict.keys())))

    thread_num = len(zj_files) / SHOW_FILES_PER_THREAD + 1
    print("show threads num: %d" % thread_num)
    show_threads = []
    for i in range(thread_num - 1):
        t = MyThread(parse_create_pushid_site_file_thread,
                     (zj_click_dict, zj_files[i * SHOW_FILES_PER_THREAD: (i + 1) * SHOW_FILES_PER_THREAD], zj_aid, "rtb_creative"),
                     parse_create_pushid_site_file_thread.__name__ + "_" + str(i))
        show_threads.append(t)
    t = MyThread(parse_create_pushid_site_file_thread,
                 (zj_click_dict, zj_files[thread_num - 1 * SHOW_FILES_PER_THREAD: len(zj_files)], zj_aid, "rtb_creative"),
                 parse_create_pushid_site_file_thread.__name__ + "_" + str(thread_num - 1))
    show_threads.append(t)
    for i in range(thread_num):
        show_threads[i].start()

    for i in range(thread_num):
        show_threads[i].join()
        temp_dict = show_threads[i].get_result()
        print("len of %s temp_dict is %d" % (show_threads[i].getName(), len(temp_dict.keys())))
        merge_total_dict(temp_dict, zj_total_dict)
        print("len after add %s temp_dict is %d" % (show_threads[i].getName(), len(zj_total_dict.keys())))

    total_dict = merge_zj_js_total_dict(zj_total_dict, js_total_dict)
    print("len of total_dict is %d" % len(total_dict.keys()))
    flush_total_dict(total_dict, log_file_name)

    #print_click_dict(zj_click_dict)
    #print_click_dict(js_click_dict)
    #parse_create_pushid_site(zj_click_dict, zj_total_dict, zj_dir_name, zj_aid)
    #print_cur_time("finish parse_create_pushid_site zhejiang is ")
    #parse_create_pushid_site(js_click_dict, js_total_dict, js_dir_name, js_aid)
    #print_cur_time("finish parse_create_pushid_site jiangsu is ")
    #print_total_dict(total_dict)
    #flush_total_dict(total_dict)
    #print_cur_time("end time is ")

if __name__ == "__main__":
    main()
