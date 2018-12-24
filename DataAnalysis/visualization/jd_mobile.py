#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: jd_mobile.py
@time: 2017/7/21 16:13
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymongo


def read_data_from_mongo(mongo_uri, mongo_db, mongo_collection):
    """
    
    :param mongo_uri: the mongo uri of the mongodb, like 127.0.0.1:19191
    :param mongo_db: the mongo db name
    :param mongo_collection: the mongo collection name
    :return: 
    """
    client = pymongo.MongoClient(mongo_uri)
    collection = client[mongo_db][mongo_collection]
    result = collection.find()
    print result.count()
    data = dict()
    for doc in result:
        ware_id = doc[u"商品ID"]
        product_info = dict()
        for key in doc.keys():
            product_info[key] = doc[key]
        data[ware_id] = product_info

    return data


if __name__ == "__main__":
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "jd"
    mongo_collection = "mobile_items"
    data = read_data_from_mongo(mongo_uri, mongo_db, mongo_collection)
    index = [u"商品ID", u"商品名称", u"京东价", u"分类ID", u"店铺ID", u"颜色分类", u"存储分类", u"商品规格", u"商品链接", u"总评价数", u"好评数", u"普通评价数",
             u"差评数"]
    df = pd.DataFrame(data, index=[u"京东价", u"商品名称"], columns=data.keys())
    df = df.transpose()
    plt.figure(figsize=(1280, 800))
    df.plot()
    picture_name = "京东手机.png"
    excel_name = "京东手机.xlsx"
    if os.path.exists(picture_name):
        os.remove(picture_name)
    if os.path.exists(excel_name):
        os.remove(excel_name)
    # plt.savefig(picture_name)
    df.to_excel(excel_writer=excel_name, sheet_name=u"京东手机")
