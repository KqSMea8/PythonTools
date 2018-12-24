""" this is for test"""
#!/usr/bin/env python

import sys
import redis
import logging

#used to connect the redis server
def my_connect(host, port, db, password):
    # r = redis.StrictRedis(host="localhost", port=12345, db=1, password='dev')
    r = redis.StrictRedis(host, port, db, password,
                          socket_timeout=5000, socket_connect_timeout=5000)
    # r.flushdb()
    clients = r.client_list()
    for client in clients:
        print(client)

    return r


def read_data_to_file(host, port, db, password, file_name):
    r = my_connect(host, port, db, password)
    with open(file_name, mode="w") as out:
        for key in r.scan_iter(count=100):
            key_type = r.type(key)
            if key_type == "string":
                out.write(key + " = " + r.get(key) + "\n")
            elif key_type == "list":
                key_len = r.llen(key)
                out.write(key + " = ")
                values = r.lrange(key, 0, key_len)
                first = True
                for value in values:
                    if first:
                        out.write(value)
                        first = False
                    else:
                        out.write(" " + value)
                out.write("\n")


def read_keytype_to_file(host, port, db, password, file_name):
    r = my_connect(host, port, db, password)
    with open(file_name, mode="w") as out:
        for key in r.scan_iter(count=100):
            key_type = r.type(key)
            out.write(key + " type is " + r.type(key) + "\n")


def clear_database(host, port, db, password):
    r = my_connect(host, port, db, password)
    ret = r.flushdb()
    if ret == True:
        ret_str = "success"
        logging.info("flush %d returns %s" % (db, ret_str))
    else:
        ret_str = "failed"
        logging.error("flush %d returns %s" % (db, ret_str))

#init the configuration of the logging module
def init_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] \
                                %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='redis_flush.log',
                        filemode='a')

def insert_data_from_file(host, port, db, password, filename):
    """
    read data from file and insert to the specified database
    """
    r = my_connect(host, port, db, password)
    with open(filename, mode="r") as infile:
        for line in infile:
            """
            The line format is key_type-key-value1;value2;value3
            """
            line=line.strip()
            segs=line.split("-")
            if (len(segs) != 3):
                logging.info("format error: {0}".format(line))
                continue
            key_type=segs[0].strip()
            key=segs[1].strip()
            values=segs[2].strip().split(";")
            if key_type=="set":
                for value in values:
                    value=value.strip()
                    r.sadd(key, value)
            elif key_type=="string":
                if (len(values) != 1):
                    logging.info("values for string exceed one, use the first one")
                #logging.info("set {0} for {1}".format(key, values[0]))
                r.set(key,values[0])

if __name__ == "__main__":
    # my_connect("61.160.200.231", 63791, 15, "bcdata@2701")
    # read_keytype_to_file("61.160.200.231", 63791, 15,
    #                       "bcdata@2701", "key.txt")
    #read_data_to_file("61.160.200.231", 63791, 15, "bcdata@2701", "key.txt")
    init_logging()
    #clear_database("localhost", 12345, 15, "dev")
    #clear_database("localhost", 12345, 0, "dev")
    clear_database("192.168.56.103", 12345, 0, "dev")
    clear_database("192.168.56.103", 12345, 1, "dev")
    insert_data_from_file("192.168.56.103", 12345, 0, "dev", "user.txt")
    insert_data_from_file("192.168.56.103", 12345, 1, "dev", "label.txt")
