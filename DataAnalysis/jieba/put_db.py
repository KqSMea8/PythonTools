#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: put_db.py
@time: 2017/2/11 下午9:00
"""

import leveldb

def put_db(filename):
    db_handle = leveldb.LevelDB("./db")
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            segs = line.split("\t")
            if (len(segs) != 3):
                continue

            if (segs[0] == "色情"):
                db_handle.Put(segs[1], "seqing")
            elif(segs[0] == "赌博"):
                db_handle.Put(segs[1], "dubo")
            else:
                db_handle.Put(segs[1], "unknown")

if __name__ == "__main__":
    put_db("result6.txt")