#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-07 11:00:47

import os
import sys
import pexpect
from pexpect import pxssh

_servers={"dsp":
    [
           "112.124.65.221,22,root,bcdata@2701",
           "112.124.65.47,22,root,ASDzxc246",
           "112.124.33.66,22,root,bcdata@2701",
           "112.124.33.110,22,root,bcdata@2701",
           #"115.29.173.86,22,root,bcdata@2701",
           "115.29.173.59,22,root,bcdata@2701",
           #"115.29.173.75,22,root,bcdata@2701",
           "115.29.175.16,22,root,bcdata@2701",
    ],
    "test": ["112.124.65.221,22,root,bcdata@2701",],
    "bidder11": ["115.29.188.63,22,root,bcdata@2701,/root"],
    "bidder12": ["115.29.175.16,22,root,bcdata@2701"],
    "zhejiang":[
        "61.160.200.199,22,root,czx-ctc@Hypo.cN",
        "61.160.200.225,22,root,t8&>}0k$^)",
        "61.160.200.231,22,root,i;6+!3v?%5",
    ],
    "guangxi":[
        "61.160.200.172,22,root,Hb!!*114118114,/root/bidder",
    ]

}

def auto_scp(region,file):
    passwd_key = '.*assword:'
    scp_str = "scp -P %s %s %s@%s:/%s/%s" 
    for item in _servers[region]:
        segs = item.split(",")
        if (len(segs) == 5):
            cmd_line = scp_str % (segs[1],file,segs[2],segs[0],segs[4],file)
        else:
            cmd_line = scp_str % (segs[1],file,segs[2],segs[0],"root", file)
        print("cmd_line is %s" % (cmd_line))
        try:
            child = pexpect.spawn(cmd_line,timeout=300)
            child.logfile = sys.stdout
            child.expect(passwd_key)
            child.sendline(segs[3])
            child.expect(pexpect.EOF) 
            print("finish scp %s to %s" % (file,segs[0]))
        except Exception as e:
            print("upload %s to %s failed,error: %s" %(file,segs[0],e))


def auto_cmd(region):
    pass


"""
get script self's name
"""
def get_script_name(argv0):
    argv0_list = argv0.split(os.sep)
    # get script file name self
    script_name = argv0_list[len(argv0_list) - 1]
    # remove ".py"
    if script_name.endswith(".py"):
        script_name = script_name[0:-3]

    return script_name

def main():
    if (len(sys.argv) != 3):
        print("Useage: %s <region name> <file_name>" %
                (get_script_name(sys.argv[0])))
        return -1
    region = sys.argv[1]
    file = sys.argv[2]
    auto_scp(region,file)

if __name__ == "__main__":
    main()
