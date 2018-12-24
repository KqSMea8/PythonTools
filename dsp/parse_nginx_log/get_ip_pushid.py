#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-06 12:57:20

"""
get ip and pushid from nginx log.
"""

import esm
import sys


def main(log_file, out_file, filters):
    index = esm.Index()
    for filter_str in filters:
        index.enter(filter_str)
    index.fix()

    with open(log_file, 'r') as readfd:
        with open(out_file, 'w') as writefd:
            for line in readfd:
                line = line.strip()
                if len(index.query(line)) != len(filters):
                    #print line
                    continue
                segs1 = line.split("\"")
                ip = segs1[6].strip()
                req_url = segs1[1].strip()
                segs2 = req_url.split("&")
                for seg in segs2:
                    seg = seg.strip()
                    if seg.find("pushid") != -1:
                        pushid = seg.strip().split("=")[1]
                        writefd.write("%s %s\n" % (pushid, ip))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s <log_file> <out_file> [filters]" % (sys.argv[0])
        exit(-1)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
