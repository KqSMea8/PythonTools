#!/usr/bin/env python
# -*-encoding:utf8 -*-
import os
import sys
import base64
import hashlib

reload(sys)
sys.setdefaultencoding("utf8")
sys.path.append(".")

import esm
import adsite


domains = set([".com",".cn",".com.cn",".gov",".net",".edu.cn",".net.cn",".org.cn",".co.jp",".gov.cn",".co.uk","ac.cn",".edu",".tv",".info",".ac",".ag",".am",".at",".be",".biz",".bz",".cc",".de",".es",".eu",".fm",".gs",".hk",".in",".info",".io",".it",".jp",".la",".md",".ms",".name",".nl",".nu",".org",".pl",".ru",".sc",".se",".sg",".sh",".tc",".tk",".tv",".tw",".us",".co",".uk",".vc",".vg",".ws",".il",".li",".nz"])

def top_domain(host):
    top = ""
    segs = host.split(".")
    if len(segs) < 2:
        return None
    host2 = "." + segs[-2] + "." + segs[-1]
    host1 = "." + segs[-1]
    if host2 in domains:
        top = segs[-3] + host2
    elif host1 in domains:
        top = segs[-2] + host1
    return top

def ip2num(ip):
    ip_int = 0 
    for i,seg in enumerate(ip.split('.')):
        ip_int |= (int(seg) << ((3-i)*8))    
    return ip_int

def load_area_ip_map(area,is_parent,area_ip_set):
    with open("nanjing_ip","r") as f:
        for line in f:
            line = line.strip()
            segs = line.split(",")
            """
            parent_name = segs[0]
            parent_id = segs[1]
            kid_id = segs[2]
            kid = segs[3]
            """
            start_ip_int = int(segs[5])
            end_ip_int = int(segs[7])
            (name,id) = (segs[0],segs[1]) if is_parent else (segs[3],segs[2])
            if area == name or id == area:
                ip_seg_len = end_ip_int - start_ip_int
                for i in range(0,ip_seg_len):
                    area_ip_set.add(start_ip_int + i)

def judge_ip(ip_file,seg_dict):
    with open(ip_file,"r") as f : 
        for line in f:
            line = line.strip()
            int_ip = ip2num(line)
            if int_ip not in seg_dict:
                print line
    

IP=0
ADSL=1
TIMESTAMP=2
URL=3
REFER=4
UA=5
DEST_IP=6
COOKIE=7


exclude_char=set("<&%$#@~!()<>{}[]")
mobile_ua=set(["like Mac OS X","Mobile","Linux; Android"])


def load_pattern_dict(engine):
    for key in adsite.adsite.keys():
        engine.enter(key)
    engine.fix()

def load_pattern_file(file,engine):
    with open(file) as f:
        for line in f:
            line = line.strip()
            engine.enter(line)
    engine.fix()

engine = esm.Index()
load_pattern_dict(engine)

black_engine = esm.Index()
load_pattern_file("black_host",black_engine)

def get_host(url):
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]
    host = url.split("/")[0]
    return host

exclude_char=set("*,<&%$#@~!()<>{}[]")
visit_map={}
for line in sys.stdin:
    line = line.strip()    
    if line=="":
        continue
    segs = line.split()
    m=hashlib.md5()
    try:
        ip=segs[IP]
        dest=segs[DEST_IP]
        adsl=segs[ADSL]
        ua = segs[UA]
        m.update(adsl) 
        m.update(ua)
        times=int(segs[TIMESTAMP])/1000
        url = segs[URL]
        refer=segs[REFER]
        if refer:
            #refer=base64.b64decode(refer)
            refer_host = get_host(refer)
            host = get_host(url)
            if black_engine.query(refer_host):
                continue 
            domain = top_domain(refer_host)
            if set(domain) & exclude_char:
                continue
            res = engine.query(host)
            if res:
                key = res[0][1]
                print domain,m.hexdigest(),times,adsite.adsite[key],url
    except Exception,e:
        continue
