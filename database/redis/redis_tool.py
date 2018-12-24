#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 10:42
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : redis_tool.py
# @Software: PyCharm
# @Description redis工具测试类

import logging
import redis


# used to connect the redis server
def my_connect(host, port, db_index, password):
    # r = redis.StrictRedis(host="localhost", port=12345, db=1, password='dev')
    redis_conn = redis.Redis(host, port, db_index, password, socket_timeout=5000)
    # r.flushdb()
    # clients = redis_conn.client_list()
    # for client in clients:
    #    print(client)

    return redis_conn


def read_data_to_file(host, port, db_index, password, file_name):
    redis_conn = my_connect(host, port, db_index, password)
    out = open(file_name, mode="w")
    key_list = redis_conn.keys()
    for key in key_list:
        key_type = redis_conn.type(key)
        if key_type == "string":
            out.write(key + "\1string\1" + redis_conn.get(key) + "\n")
        elif key_type == "list":
            key_len = redis_conn.llen(key)
            out.write(key + "\1list\1")
            values = redis_conn.lrange(key, 0, key_len)
            first = True
            for value in values:
                if first:
                    out.write(value)
                    first = False
                else:
                    out.write("\2" + value)
            out.write("\n")
        elif key_type == "hash":
            logging.info("hash key: " + key)
            out.write(key + "\1" + "hash" + "\1")
            hash_keys = redis_conn.hkeys(key)
            first = True
            for entry_key in hash_keys:
                if first:
                    out.write(entry_key + "\3" + redis_conn.hget(key, entry_key))
                    first = False
                else:
                    out.write("\2" + entry_key + "\3" + redis_conn.hget(key, entry_key))
            out.write("\n")
        elif key_type == "set":
            out.write(key + "\1set\1")
            values = set()
            while True:
                value = redis_conn.srandmember(key)
                values.add(value)
                if len(values) > 100:
                    break
            first = True
            for value in values:
                if first:
                    out.write(value)
                    first = False
                else:
                    out.write("\2" + value)
            out.write("\n")


def read_keytype_to_file(host, port, db_index, password, file_name):
    redis_conn = my_connect(host, port, db_index, password)
    out = open(file_name, mode="w")
    key_list = redis_conn.keys()
    for key in key_list:
        out.write(key + " type is " + redis_conn.type(key) + "\n")


def clear_database(host, port, db_index, password):
    redis_conn = my_connect(host, port, db_index, password)
    ret = redis_conn.flushdb()
    if ret:
        ret_str = "success"
        logging.info("flush %d returns %s" % (db_index, ret_str))
    else:
        ret_str = "failed"
        logging.error("flush %d returns %s" % (db_index, ret_str))


# init the configuration of the logging module
def init_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] \
                                %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='redis_tool.log',
                        filemode='a')


def insert_data_from_file(host, port, db_index, password, filename):
    """
    read data from file and insert to the specified database
    """
    redis_conn = my_connect(host, port, db_index, password)
    infile = open(filename, mode="r")
    for line in infile:
        """
        The line format is key_type-key-value1;value2;value3
        """
        line = line.strip()
        if (line.startswith("#") or line.startswith(";")):
            logging.info("comment line: %s" % (line))
            continue
        segs = line.split("-")
        if (len(segs) != 3):
            logging.info("format error: %s" % (line))
            continue
        key_type = segs[0].strip()
        key = segs[1].strip()
        values = segs[2].strip().split(";")
        if key_type == "set":
            for value in values:
                value = value.strip()
                redis_conn.sadd(key, value)
        # Insert data in the sequence of the input
        elif key_type == "list":
            for value in values:
                redis_conn.rpush(key, value)
        elif key_type == "string":
            if (len(values) != 1):
                logging.info("values for string exceed one, use the first one")
            # logging.info("set {0} for {1}".format(key, values[0]))
            redis_conn.set(key, values[0])


def insert_data_from_file_v2(host, port, db_index, password, filename):
    """
    read data from file and insert to the specified database
    """
    redis_conn = my_connect(host, port, db_index, password)
    infile = open(filename, mode="r")
    for line in infile:
        """
        The line format is key_type-key-value1;value2;value3
        """
        line = line.strip()
        if (line.startswith("#") or line.startswith(";")):
            logging.info("comment line: %s" % (line))
            continue
        segs = line.split("\1")
        key = segs[0].strip()
        key_type = segs[1].strip()
        values = segs[2].strip().split("\2")
        if key_type == "set":
            for value in values:
                value = value.strip()
                redis_conn.sadd(key, value)
        # Insert data in the sequence of the input
        elif key_type == "list":
            for value in values:
                redis_conn.rpush(key, value)
        elif key_type == "string":
            if (len(values) != 1):
                logging.info("values for string exceed one, use the first one")
            # logging.info("set {0} for {1}".format(key, values[0]))
            redis_conn.set(key, values[0])
        elif key_type == "hash":
            value_dict = {}
            for value in values:
                datas = value.split("\3", 2)
                value_dict[datas[0]] = datas[1]

            redis_conn.hmset(key, value_dict)


def test_op(host, port, db_index, password):
    redis_conn = my_connect(host, port, db_index, password)
    if (None != redis_conn):
        print("Connect success")

    redis_conn.set("name", "yuxuecheng")
    value = redis_conn.get("name")
    print("value of name is: %s" % value)

    redis_conn.rpush("aaa", "aaa1")
    redis_conn.rpush("aaa", "aaa2")
    aaa_len = redis_conn.llen("aaa")
    print("aaa len: %d" % aaa_len)
    result = redis_conn.lrange("aaa", 0, aaa_len)
    for aaa_value in result:
        print(aaa_value)


if __name__ == "__main__":
    # my_connect("61.160.200.231", 63791, 15, "bcdata@2701")
    # read_keytype_to_file("61.160.200.231", 63791, 15,
    #                       "bcdata@2701", "key.txt")
    # read_data_to_file("61.160.200.231", 63791, 15, "bcdata@2701", "key.txt")
    init_logging()
    # clear_database("localhost", 12345, 15, "dev")
    # clear_database("localhost", 12345, 0, "dev")
    # clear_database("192.168.56.103", 12345, 0, "dev")
    # clear_database("192.168.56.103", 12345, 1, "dev")
    # clear_database("192.168.56.103", 12345, 2, "dev")
    # insert_data_from_file("192.168.56.103", 12345, 0, "dev", "user.txt")
    # insert_data_from_file("192.168.56.103", 12345, 1, "dev", "label.txt")
    # insert_data_from_file("192.168.56.103", 12345, 2, "dev", "app_info.txt")
    # read_data_to_file("192.168.56.103", 12345, 5, "", "db5.txt")
    # insert_data_from_file_v2("192.168.56.103", 12345, 1, "", "db1.txt")
    test_op("10.37.1.215", 19000, 1, "")
