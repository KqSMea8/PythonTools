#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 10:14:14

"""
Example of glob function
"""

import glob
import os
import itertools as it

def multiple_file_types(*patterns):
    """
    use glob to search for multiple file types files
    """
    return it.chain.from_iterable(glob.glob(pattern) for pattern in patterns)

if __name__ == "__main__":
    FILES = glob.glob("*.py")
    print(FILES)

    for filename in multiple_file_types("*.txt", "*.py"):
        print(filename)

    # if you want to print the absolute path, use realpath function
    for filename in multiple_file_types("*.txt", "*.py"):
        realpath = os.path.realpath(filename)
        print("file name {0}: absolute path {1}".format(filename, realpath))
