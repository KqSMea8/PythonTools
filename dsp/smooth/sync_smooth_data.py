#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: sync_smooth_data.py
@time: 08/12/2017 17:43
"""

import time
import logging
import redis
import ConfigParser
from pymongo import MongoClient


# init the configuration of the logging module
def init_logging():
    day = int(time.strftime("%Y%m%d"))
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] \
                                %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='sync_smooth_data_%s.log' % day,
                        filemode='a')


# used to connect the redis server
def my_connect(host, port, db_index, password):
    # r = redis.StrictRedis(host="localhost", port=12345, db=1, password='dev')
    redis_conn = redis.Redis(host, port, db_index, password, socket_timeout=5000)

    return redis_conn


def get_plan_show_number(mongo_uri, db_name, collection_name, plan_ids):
    show_result = dict()
    client = MongoClient(mongo_uri)
    col = client[db_name][collection_name]
    day = int(time.strftime("%Y%m%d"))
    logging.info("DAY: %d" % day)
    cursor = col.find({"DAY": day}, {"PLANID": 1, "show": 1, "_id": 0})
    for result in cursor:
        plan_id = str(result["PLANID"])
        show_number = result["show"]
        logging.debug("plan_id: %s, show_number: %d" % (plan_id, show_number))
        if plan_id in plan_ids:
            logging.debug("plan id %s hit keys" % plan_id)
            show_result[plan_id] = show_number

    return show_result


def get_plan_ids(redis_conn):
    """
    from the redis database to get plan id
    :param redis_conn: the redis connection
    :return: the plan id set
    """
    return set(redis_conn.keys())


def update_redis_number(redis_conn, plan_show_result):
    """

    :param redis_conn: the redis connection
    :param plan_show_result: the plan show result need to update to the redis

    :return: None
    """
    for plan_id, show_number in plan_show_number.iteritems():
        result = "%s:%d:%d:%f" % (plan_id, int(time.time()), 0, show_number)
        logging.warning("update plan id: %s, result: %s" % (plan_id, result))
        redis_conn.set(plan_id, result)


if __name__ == '__main__':
    init_logging()

    config = ConfigParser.ConfigParser()
    config.read('config.conf')
    redis_host = config.get('redis', 'host')
    redis_port = int(config.get('redis', 'port'))
    redis_password = config.get('redis', 'password')
    redis_db = int(config.get('redis', 'db'))

    mongo_uri = config.get('mongo', 'uri')
    mongo_db = config.get('mongo', 'db')
    mongo_collection = config.get('mongo', 'collection')

    redis_conn = my_connect(redis_host, redis_port, redis_db, redis_password)
    plan_ids = get_plan_ids(redis_conn)
    logging.info(plan_ids)
    plan_show_number = get_plan_show_number(mongo_uri, mongo_db, mongo_collection, plan_ids)
    logging.info(plan_show_number)
    update_redis_number(redis_conn, plan_show_number)

