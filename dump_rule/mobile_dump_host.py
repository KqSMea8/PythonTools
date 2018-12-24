    #!/usr/bin/env python
# -*-encoding:utf-8 -*-

import os
import sys
import re
import json
from  MySQLdb import connect

MAX_HOST = 2000
total_host =1
black_host_set = set()
host_pattern = set()
exclude_char_set=set("^@:,>?<&$#!~()")

def load_black_host():
	with open("black_host","r") as f:
		for line in f:
			line = line.strip()    
			if line:
				black_host_set.update(line.split('.'))


def load_rule():
    conn = connect(host="180.96.26.186",port=33966,user="root",passwd="jshb114@nj",db="adp")
    #sql = "select usertags,host_set_object from adp_group_info where enable = 1"
    sql = "select a.usertags,a.host_set_object,a.plan_id from adp_group_info as a,adp_plan_info as b where a.plan_id=b.plan_id and a.enable =1 and b.enable=1 and a.mobile=2;"
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
def dump_host(f):
    global total_host
    for p in host_pattern:
		try:
			if len(p) < 2:
				continue
			if set(p) & exclude_char_set:
				continue
			if total_host > MAX_HOST:
				break
			if p.startswith("www."):
				f.write("%s\n" % p)
			elif len(p.split('.')) > 2:
				f.write("%s\n" % p)
			else:
				f.write("www.%s\n" % p)
		  	total_host +=  1
		except:
			continue

def filter_host(out,num):
    global total_host
    with open("m_host_lib","r") as f:
        for line in f:
            line = line.strip()
            try:
                host,num_ = line.split()
            except:
                continue

            if total_host > MAX_HOST:
                break

            s = set(host.split('.'))
            if len(s) < 2:
                continue
            if len(s)>2 and len(s & black_host_set) >= len(s)-1:
                continue
            elif len(s & black_host_set) == len(s):
                continue

            if set(host) & exclude_char_set:
                continue
            if host.startswith("rss."):
                continue
            """
            if host.startswith("m."):
                continue
            if host.startswith("3g."):
                continue
            """
            if host.startswith("api."):
                continue
            if "api." in host:
                continue
            if host.endswith(".com"):
                if host.endswith("hexun.com"):
                    pass
                elif len(host.split('.')) > 3:
                    continue
            elif host.endswith(".com.cn"):
                if len(host.split('.')) > 4:
                    continue

            for p in host_pattern:
                if int(num_) >= num and len(host) > 3:
                    r = p.search(host)
                    if r:
                        out.write("%s\n" % host)
                        total_host += 1
                        break
                else:
                    break
            out.write("%s\n" % host)
            total_host += 1
                        
if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
   	
    load_rule()
    load_black_host()
    output = "10043"
    with open(output,"w") as f:
        #dump_host(f)
        filter_host(f,n)
    print output
