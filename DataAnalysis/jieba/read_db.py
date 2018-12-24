#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: read_db.py
@time: 2017/2/11 下午9:31
"""

import leveldb

def read_db(target_value, filename):
    db_handle = leveldb.LevelDB("./db")
    with open(filename, "w") as f:
        for record in db_handle.RangeIter():
            key = record[0].strip()
            value = record[1].strip()
            if (value == target_value):
                f.write(key)
                f.write("\r\n")

if __name__ == "__main__":
    read_db("seqing", "seqing.txt")
    read_db("dubo", "dubo.txt")