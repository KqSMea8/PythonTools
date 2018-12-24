#!/usr/bin/env python

import os 
import sys

pre_host = None
pre_key =None
key_dict={}
flag_dict={}
pre_time=[]
key_num = {}
pre_flag = None
pre_ip = None

def print_out(refer,key_num,flag_dict):
    out_str = ""
    try:
        for k in ("1","2","3"):
            if out_str=="":
                if k in flag_dict:
                    out_str += "%d" % (int(round(float(flag_dict[k])/key_num[k])))
                else:
                    out_str += "0"
            else:
                if k in flag_dict:
                    out_str += ":%d" % (int(round(float(flag_dict[k])/key_num[k])))
                    #out_str += ":%d" % (float(flag_dict[k])/key_num[k])
                    #out_str += ":%d" % (flag_dict[k]/key_num[k])
                else:
                    out_str += ":0"
        print refer +"\t" + "\t".join(out_str.split(":"))
    except:
        pass

for line in sys.stdin:
    line = line.strip()
    segs = line.split()
    if len(segs) < 5:
        continue

    refer = segs[0]
    key = segs[1]
    times = int(segs[2])
    flag = segs[3]
    
    if pre_host != None:
        if pre_host == refer:
            if pre_key == key:
                flag_dict[flag] = flag_dict.get(flag,0) + 1
                if flag != pre_flag:
                    key_num[flag] = key_num.get(flag,0) + 1
            elif pre_key != key:
                key_num[flag] = key_num.get(flag,0) + 1
                flag_dict[flag] = flag_dict.get(flag,0) + 1
        else:
            print_out(pre_host,key_num,flag_dict)
            pre_host=refer
            pre_key =key
            flag_dict.clear()
            key_num.clear()
            flag_dict[flag] = flag_dict.get(flag,0) + 1
            key_num[flag] = 1
    else:
        pre_host = refer
        key_num[flag]= 1
        flag_dict[flag] = flag_dict.get(flag,0) + 1
        pre_key = key
    pre_flag = flag

if pre_host:
    print_out(pre_host,key_num,flag_dict) 
