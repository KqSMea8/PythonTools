#!/usr/bin/env python

"""
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""
from __future__ import print_function

import string


def get_log_file_name(log, id=""):
    month = {'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6',
             'Jul': '7', 'Aug': '8', 'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    logs_new = string.split(log, sep="[")
    segs = string.split(logs_new[1], sep="/")
    return month.get(segs[1]) + "_" + segs[0] + id + ".csv"


def get_click_log_file_name(log):
    return get_log_file_name(log, id="_click")


def get_show_log_file_name(log):
    return get_log_file_name(log, id="_show")


def flush_dict_to_file(dict_name, file_name):
    if file_name is None or len(file_name) == 0:
        return
    with open(file_name, mode="w") as wd:
        for key in dict_name.keys():
            strs = string.split(key, sep="_")
            print('%s,%s,%s' % (strs[0], strs[1], dict_name[key]), file=wd)


def parse_click_log(total_dict, file_name="click.log"):
    if total_dict is None:
        return
    """ key is adid&site, value is the times """
    log_file_name = ""
    with open(file_name, mode="r") as fd:
        for line in fd:
            if -1 == string.find(line, "click.js"):
                continue
            # print(line, end='')
            strs = string.split(line, sep="\"")
            log_file_name = get_log_file_name(strs[0])
            if (None == total_dict.get(log_file_name)):
                total_dict[log_file_name] = dict()
            # print(strs[3])
            pos = string.find(strs[3], "/", 10)
            for str in strs:
                if -1 != string.find(str, "click.js"):
                    strs2 = string.split(str, sep="&")
                    for str2 in strs2:
                        if -1 != string.find(str2, "aid"):
                            strs3 = string.split(str2, "=")
                            # print(strs3[1] + " " + strs[3][0:pos], file=wd)
                            id_site = strs3[1] + "_" + strs[3][0:pos]
                            if total_dict[log_file_name].get(id_site) == None:
                                total_dict[log_file_name][id_site] = [0, 1]
                            else:
                                total_dict[log_file_name][id_site][1] += 1
                                # flush_dict_to_file(ad_site_map, log_file_name)


def parse_show_log(total_dict, file_name="show.log"):
    if None == total_dict:
        return
    """ key is adid&site, value is the times """
    log_file_name = ""
    with open(file_name, mode="r") as fd:
        for line in fd:
            if -1 == string.find(line, "show.js"):
                continue
            # print(line, end='')
            strs = string.split(line, sep="\"")
            # print("log file name of " + strs[0] + " is " + get_log_file_name(strs[0]))
            temp_log_file_name = get_log_file_name(strs[0])
            if log_file_name != temp_log_file_name:
                # flush_dict_to_file(ad_site_map, log_file_name)
                # ad_site_map.clear()
                log_file_name = temp_log_file_name
                if (None == total_dict.get(log_file_name)):
                    total_dict[log_file_name] = dict()
            # print(strs[3])
            pos = string.find(strs[3], "/", 10)
            for str in strs:
                if -1 != string.find(str, "show.js"):
                    strs2 = string.split(str, sep="&")
                    for str2 in strs2:
                        if -1 != string.find(str2, "aid"):
                            strs3 = string.split(str2, "=")
                            # print(strs3[1] + " " + strs[3][0:pos], file=wd)
                            id_site = strs3[1] + "_" + strs[3][0:pos]
                            if total_dict[log_file_name].get(id_site) == None:
                                total_dict[log_file_name][id_site] = [1, 0]
                            else:
                                total_dict[log_file_name][id_site][0] += 1
                                # flush_dict_to_file(ad_site_map, log_file_name)


def print_total_dict(total_dict):
    for key in total_dict.keys():
        id_site_dict = total_dict[key]
        for id_site in id_site_dict.keys():
            strs = string.split(id_site, "_")
            print('%s,%s,%s,%s,%s' % (key, strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]))


def flush_total_dict(total_dict):
    for key in total_dict.keys():
        with open(key, mode="w") as logfd:
            id_site_dict = total_dict[key]
            for id_site in id_site_dict.keys():
                strs = string.split(id_site, "_")
                print('%s,%s,%s,%s' % (strs[0], strs[1], id_site_dict[id_site][0], id_site_dict[id_site][1]),
                      file=logfd)


"""
This dict's structure is as below:
the first dimension is log_file_name, the value is a dict too;
the second dimension is id_sitename, the value is a list, in which the first value is the show times, the second is the click times
"""
total_dict = dict()
parse_click_log(total_dict)
parse_show_log(total_dict)
flush_total_dict(total_dict)
