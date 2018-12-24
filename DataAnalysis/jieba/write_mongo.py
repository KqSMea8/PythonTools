#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Xuecheng Yu'
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2017-02-14 17:54:13

import sys
import os
import re
from pymongo import MongoClient
import utility
import bson

ValidIpAddressRegex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

ValidHostnameRegex = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

seqing_group_id = bson.Int64(1)
dubo_group_id = bson.Int64(2)
xiaoshuo_group_id = bson.Int64(3)
changwei_group_id = bson.Int64(4)
zhejiang_changwei_group_id = bson.Int64(88)


def write_mongo(host, port, db_name, collection_name, file_name):
    client = MongoClient(host, port)
    print client.server_info()
    dbs = client.database_names()
    print '\t'.join(dbs)
    db = client.get_database(db_name)
    collections = db.collection_names(include_system_collections=False)
    print '\t'.join(collections)
    collection = db.get_collection(collection_name)
    with open(file_name, "r") as fd:
        for line in fd:
            line = line.strip()
            segs = line.split("\t")
            if len(segs) < 2:
                continue

            host = utility.url_to_host(segs[1])
            domain = utility.host_to_domain(host)
            if ValidHostnameRegex.match(domain) is not None or ValidIpAddressRegex.match(domain) is not None:
                rule = host + "/*"
                if segs[0] == "色情":
                    collection.insert_one({"table":"domain_rule", "group_id":seqing_group_id, "domain":domain, "rule":rule})
                    print "色情", segs[1]
                elif segs[0] == "赌博":
                    collection.insert_one({"table": "domain_rule", "group_id": dubo_group_id, "domain": domain, "rule": rule})
                    print "赌博", segs[1]
                elif segs[0] == "小说":
                    collection.insert_one({"table": "domain_rule", "group_id": xiaoshuo_group_id, "domain": domain, "rule": rule})
                    print "小说", segs[1]
                elif segs[0] == "长尾":
                    collection.insert_one({"table": "domain_rule", "group_id": changwei_group_id, "domain": domain, "rule": rule})
                    print "长尾", segs[1]
                else:
                    print "其他", segs[0], segs[1]

    cursor = collection.find_one()

def write_137_mongo(host, port, db_name, collection_name, file_name):
    client = MongoClient(host, port)
    print client.server_info()
    dbs = client.database_names()
    print '\t'.join(dbs)
    db = client.get_database(db_name)
    collections = db.collection_names(include_system_collections=False)
    print '\t'.join(collections)
    collection = db.get_collection(collection_name)
    with open(file_name, "r") as fd:
        for line in fd:
            line = line.strip()
            domain, rule = line.split('\t', 1)
            collection.insert_one({"table": "domain_rule", "group_id": zhejiang_changwei_group_id, "domain": domain, "rule": rule})

if __name__ == "__main__":
    filename = sys.argv[1]
    full_filename = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + filename
    write_137_mongo("127.0.0.1", 19191, "dpc_business", "zhejiang_telecom", full_filename)