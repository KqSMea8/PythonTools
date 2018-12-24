""" this is for test"""
#!/usr/bin/env python

import logging
import redis

#used to connect the redis server
def my_connect(host, port, db_index, password):
    # r = redis.StrictRedis(host="localhost", port=12345, db=1, password='dev')
    redis_conn = redis.StrictRedis(host, port, db_index, password,
                                   socket_timeout=5000, socket_connect_timeout=5000)
    # r.flushdb()
    clients = redis_conn.client_list()
    for client in clients:
        print(client)

    return redis_conn


def read_data_to_file(host, port, db_index, password, file_name):
    redis_conn = my_connect(host, port, db_index, password)
    with open(file_name, mode="w") as out:
        for key in redis_conn.scan_iter(count=100):
            key_type = redis_conn.type(key)
            if key_type == "string":
                out.write(key + " = " + redis_conn.get(key) + "\n")
            elif key_type == "list":
                key_len = redis_conn.llen(key)
                out.write(key + " = ")
                values = redis_conn.lrange(key, 0, key_len)
                first = True
                for value in values:
                    if first:
                        out.write(value)
                        first = False
                    else:
                        out.write(" " + value)
                out.write("\n")


def read_keytype_to_file(host, port, db_index, password, file_name):
    redis_conn = my_connect(host, port, db_index, password)
    with open(file_name, mode="w") as out:
        for key in redis_conn.scan_iter(count=100):
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

#init the configuration of the logging module
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
    with open(filename, mode="r") as infile:
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
                #logging.info("set {0} for {1}".format(key, values[0]))
                redis_conn.set(key, values[0])

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
    clear_database("192.168.56.103", 12345, 2, "dev")
    insert_data_from_file("192.168.56.103", 12345, 0, "dev", "user.txt")
    insert_data_from_file("192.168.56.103", 12345, 1, "dev", "label.txt")
    insert_data_from_file("192.168.56.103", 12345, 2, "dev", "app_info.txt")
