#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: parse_rtb_log.py
@time: 2017/7/24 15:34
"""

from __future__ import print_function
import argparse
import logging
import os
import sys
import redis

import utility
import config


def init_logging(file_name):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="{0}.log".format(file_name),
                        filemode="a")


def connect_redis(host, port, db_index, password):
    """
    connect to specified redis server
    :param host: the host of the redis server
    :param port: the port of the redis server
    :param db_index: the db index of the redis server
    :param password: the password of the redis server
    :return: the StrictRedis object
    """
    redis_conn = redis.StrictRedis(host=host, port=port, db=db_index, password=password, socket_timeout=5000)

    return redis_conn


def parse_file(file_name, redis_client, ad_click_map, index):
    ad_id_index = config.get_int_value("rtb_log_index", "ad_id")
    push_id_index = config.get_int_value("rtb_log_index", "push_id")
    with open(file_name, mode="r") as fd:
        for line in fd:
            line = line.strip()
            segs = [s.strip() for s in line.split("\01")]
            if segs[0] == "rtb_creative":
                data = dict()
                value = segs[index]
                ad_id = segs[ad_id_index]
                push_id = segs[push_id_index]
                data["ad_id"] = ad_id
                data["value"] = value
                redis_client.hmset(name=push_id, mapping=data)
                redis_client.expire(name=push_id, time=360)
            elif segs[0] == "rtb_click":
                push_id = segs[push_id_index]
                value = redis_client.hget(name=push_id, key="value")
                ad_id = redis_client.hget(name=push_id, key="ad_id")
                if ad_id is None:
                    print("The ad id for push id %s not exist" % push_id, file=sys.stderr)
                    continue
                if ad_id in ad_click_map:
                    ad_click_map[ad_id].add(value)
                else:
                    value_set = set()
                    value_set.add(value)
                    ad_click_map[ad_id] = value_set


def get_click_user(log_base_dir, day, filters):
    log_dir_name = os.path.join(log_base_dir, day)
    print(log_dir_name)
    print(os.path.abspath(log_dir_name))
    print(filters)
    print(os.path.curdir)
    file_list = utility.get_file_list(log_dir_name, filters)
    print("number of log file is %d" % len(file_list))
    redis_host = config.get_value("redis_server", "host")
    redis_port = config.get_int_value("redis_server", "port")
    redis_password = config.get_value("redis_server", "password")
    db_index = config.get_int_value("redis_server", "push_id_index")
    user_id_index = config.get_int_value("rtb_log_index", "user_id")
    redis_client = connect_redis(host=redis_host, port=redis_port, db_index=db_index, password=redis_password)
    ad_click_user_map = dict()
    for file_name in file_list:
        parse_file(file_name, redis_client, ad_click_user_map, index=user_id_index)

    return ad_click_user_map


def get_click_domain(log_base_dir, day, filters):
    log_dir_name = os.path.join(log_base_dir, day)
    print(log_dir_name)
    print(os.path.abspath(log_dir_name))
    print(filters)
    print(os.path.curdir)
    file_list = utility.get_file_list(log_dir_name, filters)
    print("number of log file is %d" % len(file_list))
    redis_client = connect_redis(host="127.0.0.1", port=63791, db_index=14, password="yxc")
    ad_click_domain_map = dict()
    for file_name in file_list:
        parse_file(file_name, redis_client, ad_click_domain_map, index=22)

    return ad_click_domain_map


def get_click_pos(log_base_dir, day, filters):
    log_dir_name = os.path.join(log_base_dir, day)
    print(log_dir_name)
    print(os.path.abspath(log_dir_name))
    print(filters)
    print(os.path.curdir)
    file_list = utility.get_file_list(log_dir_name, filters)
    print("number of log file is %d" % len(file_list))
    redis_client = connect_redis(host="127.0.0.1", port=63791, db_index=13, password="yxc")
    ad_click_pos_map = dict()
    for file_name in file_list:
        parse_file(file_name, redis_client, ad_click_pos_map, index=24)

    return ad_click_pos_map


if __name__ == "__main__":
    init_logging(os.path.basename(sys.argv[0]).rstrip(".py"))
    parser = argparse.ArgumentParser(prog="get_click_user", version="%(prog)s 1.0",
                                     description="Process bidder log to find click users")
    parser.add_argument("-l", "--log-dir", dest="log_dir", required=True, help="The directory name of the log file")
    parser.add_argument("-o", "--out-dir", dest="out_dir", required=True,
                        help="The directory name of the out put directory")
    parser.add_argument("-a", "--ad-id", dest="ad_id", type=int, help="The ad id to statistic")
    parser.add_argument("-f", "--filter", dest="filters", nargs='+')

    options = parser.parse_args()

    log_dir_name = options.log_dir
    out_dir_name = options.out_dir
    ad_id = options.ad_id
    filters = options.filters

    print(log_dir_name)
    print(out_dir_name)
    print(ad_id)
    print(filters)

    if log_dir_name is None or out_dir_name is None:
        parser.print_help()
        sys.exit(-1)

    ad_click_user_map = get_click_user(".", "20170717", filters=filters)

    for ad_id in ad_click_user_map.keys():
        user_id_set = ad_click_user_map[ad_id]
        print("%s: %d: %s" % (ad_id, len(user_id_set), ",".join(user_id_set)))
