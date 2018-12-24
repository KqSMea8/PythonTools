#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: parse_log_files.py.py
@time: 2017/6/9 上午10:09
"""

import sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('.')
import os
import threading
import logging
import time
import esm
import traceback
import urllib2
import chardet
from optparse import OptionParser

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class MyThread(threading.Thread):
    """
    define self Thread class to meet the requirement
    """

    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.res = 0
        print self.name
        print self.func
        print self.args

    def run(self):
        logging.warn("starting %s at: %s" % (self.name, time.ctime()))
        self.res = self.func(*self.args)
        logging.warn("finished %s at: %s" % (self.name, time.ctime()))

    def get_result(self):
        return self.res


def init_logging():
    logging.basicConfig(level=logging.WARNING,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="parse_rtb_log.log",
                        filemode="a")


def get_file_list(dir_name, filters_list):
    if dir_name is None or 0 == len(dir_name):
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    # print(len(filters_list))
    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(
                dir_name):  # three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:  # display file information
                result = index.query(filename)
                # if len(result) == 0:
                #    continue;
                if (len(filters_list) == 0) or (len(result) == len(filters_list)):
                    files.append(os.path.join(parent, filename))
    else:
        if len(index.query(dir_name)) != 0:
            files.append(dir_name)

    return files


def parse_bidder_log_thread(es_server, file_list):
    es = Elasticsearch([es_server])
    doc_type = "rtb_log_" + time.strftime("%Y_%m_%d")
    for filename in file_list:
        if not os.path.exists(filename) and not os.path.isfile(filename):
            logging.warn("log file {0} not exist.".format(filename))
            continue
        logging.warn("parse bidder log: {0}".format(filename))
        with open(filename) as fd:
            actions = []
            bulk_num = 0
            for line in fd:
                line = line.strip()
                segs = line.split("\1")
                segs[0] = segs[0].strip()
                if segs[0] == "rtb_creative" or segs[0] == "rtb_noAd" or segs[0] == "rtb_bid":
                    data = dict()
                    data["logkey"] = segs[0]
                    data["source"] = segs[2]
                    data["exchange_user_id"] = segs[3]
                    data["requesttime"] = datetime.strptime(segs[4], "%Y-%m-%d %H:%M:%S").strftime(
                        "%Y-%m-%dT%H:%M:%S.000+0800")
                    data["userid"] = segs[5]
                    data["adid"] = int(segs[6])
                    data["pushid"] = segs[7]
                    data["clientIp"] = segs[8]
                    data["region"] = int(segs[10])
                    data["process_host"] = segs[11]
                    data["process_time"] = float(segs[12])
                    data["adsl"] = segs[14]
                    host_result = chardet.detect(segs[22])
                    data["host"] = segs[22].decode(host_result["encoding"]).encode("utf8")
                    url_result = chardet.detect(segs[23])
                    url_encoding = url_result["encoding"]
                    if url_encoding is not None and  url_encoding != "utf-8" and url_encoding != "ascii":
                        print segs[7], segs[23], url_encoding
                        data["url"] = segs[23].decode(url_encoding).encode("utf8")
                    else:
                        data["url"] = segs[23]
                    data["pos"] = segs[24]
                    data["price"] = float(segs[32])
                    data["sp"] = segs[34]
                    ua_result = chardet.detect(segs[35])
                    ua_encoding = ua_result["encoding"]
                    if ua_encoding is not None and  ua_encoding != "utf-8" and ua_encoding != "ascii":
                        print segs[7], segs[35], ua_encoding
                        data["ua"] = segs[35].decode(ua_encoding).encode("utf8")
                    else:
                        data["ua"] = segs[35]
                    data["spid"] = segs[36]
                    action = {"_index": "bidder", "_type": doc_type, "_source": data}
                    actions.append(action)
                    bulk_num += 1
                    # es.index(index="bidder", doc_type="rtb_log", body=data)
                elif segs[0] == "rtb_show" or segs[0] == "rtb_click":
                    data = dict()
                    data["logkey"] = segs[0]
                    data["source"] = segs[2]
                    data["exchange_user_id"] = segs[3]
                    data["requesttime"] = datetime.strptime(segs[4], "%Y-%m-%d %H:%M:%S").strftime(
                        "%Y-%m-%dT%H:%M:%S.000+0800")
                    data["userid"] = segs[5]
                    data["adid"] = int(segs[6])
                    data["pushid"] = segs[7]
                    data["clientIp"] = segs[8]
                    data["region"] = int(segs[9])
                    data["spid"] = segs[10]
                    action = {"_index": "bidder", "_type": doc_type, "_source": data}
                    actions.append(action)
                    bulk_num += 1
                    # es.index(index="bidder", doc_type="rtb_log", body=data)
                elif segs[0] == "stat_show" or segs[0] == "stat_click":
                    data = dict()
                    data["logkey"] = segs[0]
                    data["source"] = segs[2]
                    data["exchange_user_id"] = segs[3]
                    data["requesttime"] = datetime.strptime(segs[4], "%Y-%m-%d %H:%M:%S").strftime(
                        "%Y-%m-%dT%H:%M:%S.000+0800")
                    data["userid"] = segs[5]
                    data["adid"] = int(segs[6])
                    data["pushid"] = segs[7]
                    data["clientIp"] = segs[8]
                    data["region"] = int(segs[9])
                    data["spid"] = segs[10]
                    url_result = chardet.detect(segs[12])
                    url_encoding = url_result["encoding"]
                    if url_encoding is not None and  url_encoding != "utf-8" and url_encoding != "ascii":
                        print segs[7], segs[12], url_encoding
                        data["url"] = segs[12].decode(url_encoding).encode("utf8")
                    else:
                        data["url"] = segs[12]
                    action = {"_index": "bidder", "_type": doc_type, "_source": data}
                    actions.append(action)
                    bulk_num += 1

                elif segs[0] == "rtb_bidres":
                    data = dict()
                    data["logkey"] = segs[0]
                    data["source"] = segs[2]
                    data["exchange_user_id"] = segs[3]
                    data["requesttime"] = datetime.strptime(segs[4], "%Y-%m-%d %H:%M:%S").strftime(
                        "%Y-%m-%dT%H:%M:%S.000+0800")
                    data["userid"] = segs[5]
                    data["adid"] = int(segs[6])
                    data["pushid"] = segs[7]
                    data["clientIp"] = segs[8]
                    data["price"] = float(segs[9])
                    data["region"] = int(segs[9])
                    data["spid"] = segs[10]
                    action = {"_index": "bidder", "_type": doc_type, "_source": data}
                    actions.append(action)
                    bulk_num += 1
                    # es.index(index="bidder", doc_type="rtb_log", body=data)

                if bulk_num >= 10:
                    try:
                        bulk(es, actions, raise_on_error=True)
                        bulk_num = 0
                        actions = []
                    except UnicodeDecodeError as ude:
                        logging.error(actions)
                        logging.error(ude)
                        bulk_num = 0
                        actions = []
                    # except:
                    #     # info = sys.exc_info()
                    #     # logging.error("{0} : {1}".format(info[0], info[1]))
                    #     logging.error(traceback.print_exc())
            if bulk_num >= 0:
                try:
                    bulk(es, actions, raise_on_error=True)
                except UnicodeDecodeError as ude:
                    logging.error(actions)
                    logging.error(ude)
                # except:
                #     # info = sys.exc_info()
                #     # logging.error("{0} : {1}".format(info[0], info[1]))
                #     logging.error(traceback.print_exc())

    return 0


FILES_PER_THREAD = 1

if __name__ == "__main__":
    init_logging()
    """
    This dict's structure is as below:
    The key is pushid, value is tuple, the tuple contains access time and url
    """
    out_dir = ""
    print(sys.argv)

    parser = OptionParser()
    parser.add_option("-s", "--server", dest="server",
                      help="The server address of the Elasticsearch server, for example 192.168.56.103:9200")
    parser.add_option("-f", "--files", dest="files", action="append",
                      help="The list of the file name, this option could be specified several times")

    options, args = parser.parse_args()
    server = options.server
    file_list = list()
    if options.files is not None:
        file_list = options.files
        print(file_list)

    if server is None or len(file_list) == 0:
        parser.print_help()
        sys.exit(0)

    logging.warn("number of log file is %d" % len(file_list))

    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if (len(file_list) % FILES_PER_THREAD) != 0:
        thread_num += 1

    logging.warn("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(parse_bidder_log_thread, (server, file_list[i *
                                                                 FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD]),
                     parse_bidder_log_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(parse_bidder_log_thread, (server, file_list[(thread_num - 1) *
                                                             FILES_PER_THREAD: len(file_list)]),
                 parse_bidder_log_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        result = threads[i].get_result()
        logging.warn("{0} has finished".format(threads[i].getName()))
