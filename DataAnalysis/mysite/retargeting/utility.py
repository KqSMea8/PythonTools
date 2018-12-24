#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: utility.py.py
@time: 2017/7/24 14:29
"""

import esm
import os


def get_file_list(dir_name, filters_list):
    if dir_name is None or 0 == len(dir_name):
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    if os.path.isdir(dir_name):
        for parent, _, file_names in os.walk(dir_name):
            # three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in file_names:
                # display file information
                result = index.query(filename)
                if len(result) == 0:
                    continue
                files.append(os.path.join(parent, filename))
    else:
        if len(index.query(dir_name)) != 0:
            files.append(dir_name)

    return files


