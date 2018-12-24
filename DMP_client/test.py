#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-08-17 14:31:22

import os
import sys

filename = "client.py"
if os.path.exists(filename):
    local_path = os.path.curdir
    print (local_path)
    file_handler = open(os.path.join(local_path, filename), 'r')
    for line in file_handler:
        print(line.strip())

    file_handler.close()
