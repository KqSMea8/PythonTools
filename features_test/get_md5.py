#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-05-07 11:50:21

from __future__ import print_function

import sys
import os
import hashlib


if __name__ == "__main__":
    ua_file = ""
    md5_file = ""
    if len(sys.argv) != 3:
        print("Usage: {0} <ua file name> <out file name>".format(sys.argv[0]))
        sys.exit(-1)

    ua_file = sys.argv[1]
    md5_file = sys.argv[2]

    with open(ua_file, "r") as readfd:
        with open(md5_file, "w") as writefd:
            for line in readfd:
                line = line.strip()
                m = hashlib.md5()
                m.update(line)
                md5str = m.hexdigest()
                print("{0}:{1}".format(md5str, line), file=writefd)



