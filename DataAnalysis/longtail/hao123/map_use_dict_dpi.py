#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import sys
import traceback
import re

sys.path.append('.')


domains = set(
    [".com", ".cn", ".com.cn", ".gov", ".net", ".edu.cn", ".net.cn", ".org.cn", ".co.jp", ".gov.cn", ".co.uk", "ac.cn",
     ".edu", ".tv", ".info", ".ac", ".ag", ".am", ".at", ".be", ".biz", ".bz", ".cc", ".de", ".es", ".eu", ".fm", ".gs",
     ".hk", ".in", ".info", ".io", ".it", ".jp", ".la", ".md", ".ms", ".name", ".nl", ".nu", ".org", ".pl", ".ru",
     ".sc", ".se", ".sg", ".sh", ".tc", ".tk", ".tv", ".tw", ".us", ".co", ".uk", ".vc", ".vg", ".ws", ".il", ".li",
     ".nz", ".me", ".xin", ".pw"])

white_pat = None
black_pat = None


def init_white_pattern():
    global white_pat
    regexs = set()
    with open("white_host", "r") as fd:
        for line in fd:
            line = line.strip()
            line = line.replace("*", ".*").replace("?", "\?")
            line = "^" + line +"$"
            regexs.add(line)

    #print(regexs)
    white_pat = re.compile("|".join(list(regexs)))


def init_black_pattern():
    global black_pat
    regexs = set()
    with open("black_host", "r") as fd:
        for line in fd:
            line = line.strip()
            line = line.replace("*", ".*").replace("?", "\?")
            line = "^" + line + "$"
            regexs.add(line)

    #print(regexs)
    black_pat = re.compile("|".join(list(regexs)))


def top_domain(host):
    top = ""
    suffix = ""
    segs = host.split(".")
    if len(segs) < 2:
        return top, suffix
    host2 = "." + segs[-2] + "." + segs[-1]
    host1 = "." + segs[-1]
    if host2 in domains:
        top = segs[-3] + host2
        suffix = host2
    elif host1 in domains:
        top = segs[-2] + host1
        suffix = host1
    return top, suffix


def url_format(url):
    url = url.strip("/ ")
    if url[0:7] == "http://":
        url = url[7:]
    if url[0:4] == "www.":
        url = url[4:]
    return url


def load_dict(filename, ip_dict):
    with open(filename, 'r') as fd:
        for line in fd:
            line = line.strip()
            if line == "":
                continue
            segs = line.split(',')
            if len(segs) == 3:
                ip_dict[segs[0]] = segs[2]


exclude_char = set("*,<&%$#@~!^()<>*{}\"\'[]=+|\\")
ip_dict = {}


# loadDict('ip_adsl',ip_dict)
# for host in cate_dict:
#    print host, cate_dict[host]

def load_host(file, host_map):
    with open(file) as f:
        for line in f:
            line = line.strip()
            segs = line.split("\t", 1)
            host_map[segs[0]] = segs[1]

IP = 0
ADSL = 1
TIMESTAMP = 2
URL = 3
REFER = 4
UA = 5
DEST_IP = 6
COOKIE = 7

# host_map={}
# load_host("adsite",host_map)
init_white_pattern()
init_black_pattern()
host_count = {}
for line in sys.stdin:
    line = line.strip()
    if line == "":
        continue
    segs = line.split("\t")
    if len(segs) < 8:
        continue
    try:
        url = segs[URL]
        ip = segs[IP]
        ua = segs[UA]
        #print(url)
        #print(ip)
        #print(ua)
        """
        if ua.find("iPhone") <0 and ua.find("Android")<0:
                continue
        """
        if url.find("www.hao123.com") < 0:
            continue
        m = hashlib.md5()
        m.update(ip)
        m.update(ua)
        key = m.hexdigest()
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]

        if white_pat.match(url) is None:
            #print("{0} is not in white".format(url))
            url = "$" + url
            continue

        if black_pat.match(url):
            #print("{0} is in black".format(url))
            url = "&" + url

        #print url
        if url[0] != '&':
            host = url.split("/", 1)[0]
        else:
            host = url

        if host.find("www.hao123.com") < 0:
            continue

        if set(host) & exclude_char and (set(host[0]) & exclude_char is None):
            #print(url + "continue 1111")
            continue

        if len(host.split('.')) < 5:
            if host and host in host_count:
                #print(host + " add 1")
                host_count[host]["pv"] = host_count[host]["pv"] + 1
                host_count[host]["key_set"].add(key)
                host_count[host]["ip_set"].add(ip)
            elif host:
                #print(host + " initialize")
                t = {
                    "pv": 1,
                    "key_set": set([key]),
                    "ip_set": set([ip]),
                }
                host_count[host] = t
    except:
        traceback.print_exc()
        continue
else:
    try:
        """
            for k,v in host_count.iteritems(): 
                print "%s\t%d\t%d\t%d" % (k,v["pv"],len(v["key_set"]),len(v["ip_set"]))
        """
        for k, v in host_count.iteritems():
            print("%s\t%d\t%d\t%d" % (k,v["pv"],len(v["key_set"]),len(v["ip_set"])))
    except TypeError as te:
        traceback.print_exc()
        pass
