#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: logstats.py
@time: 08/11/2017 13:21
"""


import sys
import logging
import os
import time
from optparse import OptionParser

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout


def init_logging(filename):
    filename = os.path.join("logs", filename)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename=filename,
                        filemode="a")


def get_count(es, doc_type):
    result = es.count(index='bidder', doc_type=doc_type, body='{"query":{"match_all":{}}}')
    return result['count']


def del_func(host, port, user, password, doc_type):
    logging.info("del_func start")
    logging.info("doc_type: %s" % doc_type)
    # es = Elasticsearch(["10.54.8.71:9200"])
    es = Elasticsearch([host], http_auth=(user, password), port=port)
    count = 1
    while count > 0:
        try:
            params = {"refresh": True}
            es.delete_by_query(index='bidder', body='{"query":{"match_all":{}}}', doc_type=doc_type, params=params)
            count = get_count(es, doc_type)
        except ConnectionTimeout as e:
            logging.warn(e)
            count = 1  # 为了让循环不退出
            continue


if __name__ == '__main__':
    log_file_name = "log_del_%s.log" % time.strftime("%Y-%m-%d")
    init_logging(log_file_name)
    parser = OptionParser()
    parser.add_option("--host", dest="host",
                      help="The server address of the Elasticsearch server, for example 192.168.56.103")
    parser.add_option("--port", dest="port", type=int,
                      help="The server port of the Elasticsearch server, for example 9200")
    parser.add_option("-u", "--user", dest="user",
                      help="The user of the Elasticsearch server")
    parser.add_option("--password", dest="password",
                      help="The password of the Elasticsearch server")
    parser.add_option("-d", "--doc-type", dest="doctype", help="The day of log, for example rtb_log_2017_10_11")
    # parser.add_option("-f", "--files", dest="files", action="append",
    #                   help="The list of the file name, this option could be specified several times")

    options, args = parser.parse_args()
    host = options.host
    port = options.port
    user = options.user
    password = options.password
    doc_type = options.doctype

    logging.info("host: %s, port: %d, doc type: %s" % (host, port, doc_type))
    if user is not None and password is not None:
        logging.info("user: %s, password: %s" % (user, password))
    elif user is None and password is None:
        logging.warning("user and password is None")
        user=""
        password=""
    else:
        parser.print_help()
        sys.exit(0)

    if host is None or port is None or doc_type is None:
        parser.print_help()
        sys.exit(0)


    del_func(host, port, user, password, doc_type)


