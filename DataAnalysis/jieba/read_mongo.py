#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: read_mongo.py
@time: 2017/2/15 下午4:30
"""
from pymongo import MongoClient
import re

ValidIpAddressRegex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

ValidHostnameRegex = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")


def read_domain_from_mongo(host, port, db_name, collection_name):
    client = MongoClient(host, port)
    db = client.get_database(db_name)
    collection = db.get_collection(collection_name)
    for doc in collection.find({"table":"domain_rule", "group_id":2}):
        domain = doc["domain"]
        rule = doc["rule"]
        try:
            if domain is not None and rule is not None:
                if ValidHostnameRegex.match(domain) is not None or ValidIpAddressRegex.match(domain) is not None:
                    print '\t'.join([domain, rule])
        except TypeError:
            print domain, rule
            continue
        except UnicodeEncodeError:
            print domain, rule
            continue

if __name__ == "__main__":
    read_domain_from_mongo("127.0.0.1", 19191, "dpc_business", "zhejiang_telecom")