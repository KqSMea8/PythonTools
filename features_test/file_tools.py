#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-01 10:35:46

import os

def get_file_list(dir_name):
    if (None == dir_name or 0 == len(dir_name)):
        return None

    files = []
    if (os.path.isdir(dir_name)):
        # Three paramters return: 1.parent directory, 2. directorys, 3.files
        for parent, dirnames, filenames in os.walk(dir_name):
            # display file information
            for filename in filenames:
                files.append(os.path.join(parent, filename))
    else:
        files.append(dir_name)

    return files
