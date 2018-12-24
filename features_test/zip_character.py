#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 11:00:57

"""
Example for zip characters
"""

import zlib

def zlib_characters(content):
    print("Original content: {0}".format(content))
    print("Original Size: {0}".format(len(content)))

    compressed = zlib.compress(content)
    #print("Compressed contents: {0}".format(compressed))
    print("Compressed Size: {0}".format(len(compressed)))

    decompressed = zlib.decompress(compressed)
    print("Decompressd contents: {0}".format(decompressed))
    print("Decompressed Size: {0}".format(len(decompressed)))

if __name__ == "__main__":
    with open("glob_test.py", "r") as read_fd:
        for line in read_fd:
            zlib_characters(line)
