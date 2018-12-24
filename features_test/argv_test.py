#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: argv_test.py
@time: 2017/7/24 15:43
"""

import sys
import os


if __name__ == "__main__":
    abs_script_file_name = sys.argv[0]
    file_name = os.path.basename(abs_script_file_name)
    print file_name.rstrip(".py")