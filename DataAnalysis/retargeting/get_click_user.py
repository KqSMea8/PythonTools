#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: get_click_user.py
@time: 2017/7/24 15:34
"""

import argparse
import logging
import os
import sys
import redis

import utility


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


def parse_file(file_name, redis_client, ad_click_user_map):
    with open(file_name, mode="r") as fd:
        for line in fd:
            line = line.strip()
            segs = [s.strip() for s in line.split("\01")]
            if segs[0] == "rtb_creative":
                data = dict()
                req_time = segs[4]
                ad_id = segs[6]
                push_id = segs[7]
                client_ip = segs[8]
                user_id = segs[14]
                data["request_time"] = req_time
                data["ad_id"] = ad_id
                data["client_ip"] = client_ip
                data["user_id"] = user_id
                redis_client.hmset(name=push_id, mapping=data)
                redis_client.expire(name=push_id, time=360)
            elif segs[0] == "rtb_click":
                push_id = segs[7]
                user_id = redis_client.hget(name=push_id, key="user_id")
                ad_id = redis_client.hget(name=push_id, key="ad_id")
                if ad_id is None:
                    logging.error("The ad id for push id %s not exist" % push_id)
                    continue
                if ad_id in ad_click_user_map:
                    ad_click_user_map[ad_id].add(user_id)
                else:
                    user_id_set = set()
                    user_id_set.add(user_id)
                    ad_click_user_map[ad_id] = user_id_set


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

    file_list = utility.get_file_list(dir_name=log_dir_name, filters_list=filters)
    logging.info("number of log file is %d" % len(file_list))
    # print(file_list)
    redis_client = connect_redis(host="127.0.0.1", port=63791, db_index=1, password="yxc")
    ad_click_user_map = dict()
    for file_name in file_list:
        parse_file(file_name, redis_client, ad_click_user_map)

    for ad_id in ad_click_user_map.keys():
        user_id_set = ad_click_user_map[ad_id]
        print("%s: %d: %s" % (ad_id, len(user_id_set), ",".join(user_id_set)))
