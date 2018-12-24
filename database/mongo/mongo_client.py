#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 10:47
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : mongo_client.py
# @Software: PyCharm
# @Description mongo client测试类

from pymongo import MongoClient
import sys


def print_base_info(client):
    # Get a list of the names of all databases on the connected server.
    print("client.database_names(): {}".format(client.database_names()))
    # Get information about the MongoDB server we're connected to.
    print("client.server_info(): {}".format(client.server_info()))
    # Get the database named in the MongoDB connection URI.
    print("client.get_default_database(): {}".format(client.get_default_database()))
    # Get a :class:`~pymongo.database.Database` with the given name and options.
    print("client.get_database('StatV5'): {}".format(client.get_database('StatV5')))


def query_area_detail(db):
    coll = db.get_collection('AreaDetail')
    # To return all documents in a collection, call the find() method without a
    # criteria document
    # cursor = coll.find()
    # for document in cursor:
    #     print(document)
    # cursor.close()

    # Query by a Top Level Field
    # The following operation finds documents whose ADID field equals 2029.
    cursor = coll.find({"ADID": 2029})
    for document in cursor:
        print(document)
    cursor.close()
    print("==================================================")

    # The following operation finds documents whose DAY field greator than  20160529.
    cursor = coll.find({"DAY": {"$gt": 20160529}})
    for document in cursor:
        print(document)
    cursor.close()


def query_adspace_detail(db):
    coll = db.get_collection('AreaDetail')
    # Query by a Top Level Field
    # The following operation finds documents whose ADID field equals 2029.
    cursor = coll.find({"ADID": 2029})
    for document in cursor:
        print(document)
    cursor.close()
    print("==================================================")

    # The following operation finds documents whose DAY field greator than  20160529.
    cursor = coll.find({"DAY": {"$gt": 20160529}})
    for document in cursor:
        print(document)
    cursor.close()


def query_collection(collection_name, condition):
    """
    collection_name: the Collection to be query
    condition: the query dict for the Query operation, it must be a dict
    """
    print("======================== {} ======================".format(collection_name))
    coll = db.get_collection(collection_name)
    # Query by a Top Level Field
    cursor = coll.find(condition)
    max_num = 0
    for document in cursor:
        print(document)
        max_num = max_num + 1
        if max_num > 10:
            break
    cursor.close()

    # The following operation finds documents whose DAY field greator than  20160529.
    # cursor = coll.find({"$and":
    #    [{"DAY":{"$gte":20160317}},{"DAY":{"$lte":20160320}}]})
    # for document in cursor:
    #    print(document)
    # cursor.close()
    print("======================== {} ======================".format(collection_name))


if __name__ == '__main__':
    client = MongoClient("mongodb://120.27.150.186:12331/StatV5")
    print_base_info(client)
    db = client.get_database('sdpp_4mp_exp_temp')
    query_condition = dict()
    query_condition["date"] = {"gt": ""}
    collections = db.collection_names()
    for collection in collections:
        print(collection)
        query_collection(collection, query_condition)
    print("==================================================")
