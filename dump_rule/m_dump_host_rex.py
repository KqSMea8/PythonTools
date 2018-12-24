#!/usr/bin/env python
# -*-encoding:utf-8 -*-

import os
import sys
import re
import json
from  MySQLdb import connect

MAX_HOST = 5000
total_host = 0

black_host_set ={}
host_pattern = set()
exclude_char_set=set("^@:,>?<&$#!~()")
lib_file = "m_host_lib_10"

def load_black_host():
    with open("black_host","r") as f:
        for line in f:
            line = line.strip()
            if line:
                segs = line.split(".")
                index = len(segs)
                if index in black_host_set:
                    black_host_set[index].update(segs)
                else:
                    t = set()
                    t.update(segs)
                    black_host_set[index] = t

def load_rule():
    conn = connect(host="180.96.26.186",port=33966,user="root",passwd="jshb114@nj",db="adp")
    #sql = "select usertags,host_set_object from adp_group_info where enable = 1"
    sql = "select a.usertags,a.host_set_object,a.plan_id from adp_group_info as a,adp_plan_info as b where a.plan_id=b.plan_id and a.enable =1 and b.enable=1 and a.group_id != 211 and a.group_id != 210 and a.mobile=2;"
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    for it in res:
        usertags = it[0]
        json_host = json.loads(it[1])
        host_list = json_host["_include_host"]
        for host in host_list:
            if len(host) > 4:
                if host.startswith("*."):
                    host = host[2:]
                    host=".*\." + host
                elif host.startswith("*"):
                    host = host[1:]
                    host=".*\." + host
                if host.endswith("/*"):
                    host = host[0:-2]
                    host = host + '$'
                elif host.endswith("*"):
                    host = host[0:-1]
                    host = host + '$'
                elif host.endswith("/"):
                    host = host[0:-1]
                    host = host + '$'
                pattern_init(host)

    conn.close()

def pattern_init(host):
    host_pattern.add(re.compile(host,flags=re.I))

#direct dump host
def dump_host(out):
    global total_host
    total = 100
    i = 1
    char_set = set("abcdefghigklmnopqrstuvwxyz")
    with open(lib_file,"r") as f:
        for line in f:
            if total_host > MAX_HOST or i > total:
                break

            line = line.strip()
            if line == "":
                continue
            segs = line.split()
            if len(segs) != 2:
                continue
            num = int(segs[1])

            if not (set(segs[0]) & char_set):
                continue

            if num > 50000 and num < 200000 and not is_black_host(segs[0]):
                out.write("%s\n" % segs[0]) 
                i += 1  
                total_host += 1

            

def is_black_host(host):
    segs = host.split('.')
    index = len(segs)
    s = set(segs)
    if index < 2:
        return True

    if index in black_host_set and len(s & black_host_set[index]) >= index:
        return True
    if index-1 in black_host_set and len(s & black_host_set[index-1]) >= index-1:
        return True

    if set(host) & exclude_char_set:
        return True

    if host.startswith("rss."):
        return True
    """
    if host.startswith("wap."):
        return True
    if host.startswith("mobile."):
        return True
    if host.startswith("m."):
        return True
    if host.startswith("3g."):
        return True
    """
    if host.startswith("api."):
        return True
    if "api." in host:
        return True
    if host.endswith(".com"):
        if host.endswith("hexun.com"):
            return  False
        elif len(host.split('.')) > 3:
            return True
    elif host.endswith(".com.cn"):
        if len(host.split('.')) > 4:
            return True

def filter_host(out,num):
    global total_host
    with open(lib_file,"r") as f:
        for line in f:
            if total_host > MAX_HOST:
                break

            line = line.strip()
            try:
                host,num_ = line.split()
            except:
                continue

            if is_black_host(host):
                continue

            if int(num_) >= num and len(host) > 3:
                for p in host_pattern:
                    r = p.search(host)
                    if r:
                        out.write("%s\n" % host)
                        total_host += 1
                        break

if __name__ == "__main__":
    n = 1
    if len(sys.argv) == 2:
        lib_file = sys.argv[1]
    elif len(sys.argv) ==3:
        lib_file = sys.argv[1]
        n = int(sys.argv[2])

    load_rule()
    load_black_host()
    output = "10043"
    with open(output,"w") as f:
        filter_host(f,n)
        #dump_host(f)
    print output
