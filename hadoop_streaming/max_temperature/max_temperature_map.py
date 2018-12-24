#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-20 16:38:28

import re
import sys

for line in sys.stdin:
    val = line.strip()
    (year,temp) = (val[0:4],val[13:19])
    if temp != "+9999":
        print "%s\t%s" % (year,temp)

