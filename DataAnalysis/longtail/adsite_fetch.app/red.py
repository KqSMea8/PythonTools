#!/usr/bin/env python

import os 
import sys

pre_host = None
pre_key =None
key_dict={}
flag_dict={}
pre_time=[]

def print_out(refer,key_dict):
    for key in key_dict:
        for k,v in key_dict[key].items():
            print refer,key,k,v

for line in sys.stdin:
    line = line.strip()
    segs = line.split()
    if len(segs) < 5:
        continue

    refer = segs[0]
    key = segs[1]
    times = segs[2]
    flag = segs[3]
    
    if pre_host != None:
        if pre_host == refer:
            if pre_key == key:
                if abs(int(time) - max(pre_time)) > 10:
                    continue
                else:
                    flag_dict[flag] = flag_dict.get(flag,0) + 1
            elif pre_key != key:
                pre_time=[]
                flag_dict.clear()
                key_dict[pre_key] = flag_dict
                pre_time.append(times)
                flag_dict[flag] = flag_dict.get(flag,0) + 1
        else:
            print_out(pre_host,key_dict)
            pre_host=refer
            pre_key =key
            key_dict.clear()
            flag_dict.clear()
            pre_time = []
            flag_dict[flag] = flag_dict.get(flag,0) + 1
            pre_time.append(times)
    else:
        pre_host = refer
        pre_time.append(times) 
        flag_dict[flag] = flag_dict.get(flag,0) + 1
        pre_key = key

if pre_host:
    print_out(pre_host,key_dict) 
