#!/usr/bin/env python

import os 
import sys

domains = set([".com",".cn",".com.cn",".gov",".net",".edu.cn",".net.cn",".org.cn",".co.jp",".gov.cn",".co.uk","ac.cn",".edu",".tv",".info",".ac",".ag",".am",".at",".be",".biz",".bz",".cc",".de",".es",".eu",".fm",".gs",".hk",".in",".info",".io",".it",".jp",".la",".md",".ms",".name",".nl",".nu",".org",".pl",".ru",".sc",".se",".sg",".sh",".tc",".tk",".tv",".tw",".us",".co",".uk",".vc",".vg",".ws",".il",".li",".nz"])


def top_domain(host):
    top = ""
    suffix = ""
    segs = host.split(".")
    if len(segs) < 2:
        return top,suffix
    host2 = "." + segs[-2] + "." + segs[-1]
    host1 = "." + segs[-1]
    if host2 in domains:
        top = segs[-3] + host2
        suffix = host2
    elif host1 in domains:
        top = segs[-2] + host1
        suffix = host1
    return top,suffix

cur_host = None
host = None
cur_pv = 0
cur_uv = 0
cur_ip = 0


def load_host(file,host_map):
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    segs = line.split("\t",1)
                    host_map[segs[0]] = segs[1]
                except:
                    pass

#host_map={}
#load_host("adsite_out",host_map) 

for line in sys.stdin:
    line = line.strip()
    segs = line.split("\t",3)
    if len(segs) < 4:
        continue
    host = segs[0]
    t_pv = int(segs[1])
    t_uv = int(segs[2])
    t_ip = int(segs[3])
    
    if cur_host == host:
        cur_pv += t_pv
        cur_uv += t_uv
        cur_ip += t_ip
    else:
        if cur_host:
            print "%s\t%d\t%d\t%d" % (cur_host,cur_pv,cur_uv,cur_ip)         
            cur_host = host
            cur_pv = t_pv
            cur_uv = t_uv
            cur_ip = t_ip
        else:
            cur_host = host
            cur_pv = t_pv
            cur_uv = t_uv
            cur_ip = t_ip
    
if cur_host:
    print "%s\t%d\t%d\t%d" % (cur_host,cur_pv,cur_uv,cur_ip)         
