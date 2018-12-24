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

import os
import sys
import time
import threading
import logging
import chardet
import esm
from optparse import OptionParser
from db import DbUtil

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

domain_suffix = set()
show_detail = {}
flush_detail = {}
ad_map = dict()
city_provice_map = dict()
parse_error_num = 0
bulk_failed_num = 0
pushid_dup_num = 0
userid_null_num = 0

curr_time = 0

LOG_KEY = 0
TIME = 4
AD = 6
PUSHID = 7
IP = 8
CITY = 10
BIDDER = 11
USER = 14
HOST = 22
SP = 24
URL = 25
PRICE = 32
UA = 35
# 以后要加
NET= 40
LACCI= 0


def init_logging(filename):
    filename = os.path.join("logs", filename)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename=filename,
                        filemode="a")


def timer_func(interval):
    logging.info("timer thread start")
    global show_detail
    global flush_detail
    global curr_time
    while True:
        remaining = interval - int(curr_time) % interval
        time.sleep(remaining)
        mutex.acquire()
        logging.info("timer_func acquired mutex")
        for k, v in show_detail.items():
            # print "now:%d,v:%d" % (now,int(v["time"]))
            if curr_time - int(v["time_val"]) > 60 or _FIN == 1:
                # logging.info("2:%s,%d,%s,%s" % (v["uid"], int(v["aid"]), k, day))
                if k in show_detail:
                    flush_detail[k] = show_detail.pop(k)
        else:
            mutex.release()
            logging.info("timer_func released mutex")

        if _FIN == 1 and len(show_detail) == 0:
            logging.warning("flush show detail finished. timer_func exit")
            exit()


def flush_func(interval, host, port, user, password):
    logging.info("flush thread start")
    global flush_detail
    global show_detail
    global bulk_failed_num
    # es = Elasticsearch(["10.54.8.71:9200"])
    es = Elasticsearch([host], http_auth=(user, password), port=port)
    while True:
        actions = []
        bulk_num = 0
        mutex.acquire()
        logging.info("flush_func acquired mutex")
        for k, v in flush_detail.items():
            logging.debug("flush key: %s, value: %s" % (k, dict(v)))
            doc_type = "rtb_log_" + time.strftime("%Y_%m_%d", time.localtime(curr_time))
            if "time_val" in v:
                doc_type = "rtb_log_" + time.strftime("%Y_%m_%d", time.localtime(v["time_val"]))
                del v["time_val"]
            action = {"_index": "bidder", "_type": doc_type, "_source": v}
            logging.debug("doc_type: %s" % doc_type)
            actions.append(action)
            flush_detail.pop(k)
            bulk_num += 1
            if bulk_num >= 1000:
                try:
                    bulk(es, actions, raise_on_error=True, request_timeout=30)
                    bulk_num = 0
                    actions = []
                except UnicodeDecodeError as ude:
                    bulk_failed_num += len(actions)
                    logging.error(actions)
                    logging.error(ude)
                    bulk_num = 0
                    actions = []
        else:
            if bulk_num >= 0:
                try:
                    bulk(es, actions, raise_on_error=True, request_timeout=30)
                except UnicodeDecodeError as ude:
                    bulk_failed_num += len(actions)
                    logging.error(actions)
                    logging.error(ude)
            mutex.release()
            logging.info("flush_func released mutex")

        time.sleep(interval)
        if _FIN == 1 and len(show_detail) == 0 and len(flush_detail) == 0:
            logging.warning("flush finished. flush_func exit")
            exit()


mutex = threading.Lock()
# day = sys.argv[1]
_FIN = 0


def get_file_list(dir_name, filters_list):
    """

    :rtype: set
    """
    if dir_name is None or 0 == len(dir_name):
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = set()
    # print(len(filters_list))
    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(
                dir_name):  # three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:  # display file information
                result = index.query(filename)
                # if len(result) == 0:
                #    continue;
                if (len(filters_list) == 0) or (len(result) == len(filters_list)):
                    files.add(os.path.join(parent, filename))
    else:
        if len(index.query(dir_name)) != 0:
            files.add(dir_name)

    return files


def get_network(net):
    if net == "3":
        return "3G"
    elif net == "4":
        return "4G"
    else:
        return "Unknown"


def load_domain_suffix():
    global domain_suffix
    with open("domain.txt", mode='r') as fd:
        for suffix in fd:
            suffix = suffix.strip()
            domain_suffix.add(suffix)

    for s in domain_suffix:
        print s


def host_to_domain(host):
    """
    convert a host to domain: like: m.jd.com ==> jd.com
    this function is very slow
    :param host: the input host
    :return: the domain
    """
    global domain_suffix
    try:
        host, port = host.split(':')
    except ValueError:
        host, port = host, None
    segs = host.split('.')
    if len(segs) == 4 and ''.join(segs).isdigit():
        return host
    else:
        domain_tokens = []
        for token in segs[::-1]:
            domain_tokens.append(token)
            if token not in domain_suffix:
                break
        return '.'.join(domain_tokens[::-1])


def parse_line(line):
    global show_detail
    global flush_detail
    global curr_time
    global ad_map
    global city_provice_map
    global parse_error_num
    global pushid_dup_num
    global userid_null_num

    line = line.strip()
    segs = [seg.strip() for seg in line.split("\1")]
    try:
        if segs[TIME]:
            curr_time = time.mktime(time.strptime(segs[TIME], "%Y-%m-%d %H:%M:%S"))
    except IndexError:
        parse_error_num += 1
        return
    except ValueError:
        parse_error_num += 1
        return

    if segs[LOG_KEY] == "rtb_creative":
        if len(segs) < 40:
            logging.info("wrong creative log: " + line)
            return
        push_id = segs[PUSHID]
        # USER ID为空的比较多
        if not segs[USER]:
            userid_null_num += 1
            pass
        if push_id in show_detail:
            pushid_dup_num += 1
            show_detail[push_id]["uid"] = segs[USER]
            show_detail[push_id]["aid"] = segs[AD]
            show_detail[push_id]["show"] = 0
            show_detail[push_id]["click"] = 0
        else:
            host = segs[HOST]
            host_result = chardet.detect(host)
            host_encoding = host_result["encoding"]
            if host_encoding is None:
                logging.warn("host: " + host + " has no encoding")
            if host_encoding is not None and host_encoding != "utf-8" and host_encoding != "ascii":
                try:
                    host = host.decode(host_encoding).encode("utf8")
                except UnicodeDecodeError as ude:
                    logging.error("host: " + host + ". message: " + ude.message)
                    pass

            domain = ""
            if host is not None and len(host) > 0:
                domain = host_to_domain(host)

            url = segs[URL]
            url_result = chardet.detect(url)
            url_encoding = url_result["encoding"]
            if url_encoding is not None and url_encoding != "utf-8" and url_encoding != "ascii":
                try:
                    url = url.decode(url_encoding).encode("utf8")
                except UnicodeDecodeError as ude:
                    logging.error("url: " + url + ". message: " + ude.message)
                    pass

            ua = segs[UA]
            ua_result = chardet.detect(ua)
            ua_encoding = ua_result["encoding"]
            if ua_encoding is not None and ua_encoding != "utf-8" and ua_encoding != "ascii":
                try:
                    ua = ua.decode(ua_encoding).encode("utf8")
                except UnicodeDecodeError as ude:
                    logging.error("ua: " + ua + ". message: " + ude.message)
                    pass

            city_id = -1
            adid = -1
            campaign = -1
            policy = -1
            city = ""
            province = ""
            net = ""
            try:
                if segs[CITY] != "" and segs[CITY].isdigit():
                    city_id = int(segs[CITY])
                if segs[AD] != "" and segs[AD].isdigit():
                    adid = int(segs[AD])
                if adid != 0 and adid != -1:
                    campaign = ad_map[adid]["plan_id"]
                    policy = ad_map[adid]["group_id"]
                if city_id != 0 and city_id != -1:
                    city = city_provice_map[city_id]["city_name"]
                    province = city_provice_map[city_id]["province_name"]
                logging.debug("city id: %d, city_name: %s, province_name: %s" % (city_id, city, province))
            except KeyError as ke:
                logging.error(ke.message)
                pass
            except ValueError as ve:
                logging.error(ve)
                pass

            try:
                net = get_network(segs[NET])
            except IndexError as ie:
                logging.error(ie.message)
                pass

            try:
                show_detail[push_id] = {
                    "uid": segs[USER],
                    "ip": segs[IP],
                    "aid": adid,
                    "campaign": campaign,
                    "policy": policy,
                    "city_id": city_id,
                    "city": city,
                    "province": province,
                    "sp": segs[SP],
                    "network": net,
                    # "time": datetime.strptime(segs[TIME], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S.000+0800"),
                    # 下面这个是印尼时区
                    "time": datetime.strptime(segs[TIME], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S.000+0700"),
                    "time_val": time.mktime(time.strptime(segs[TIME], "%Y-%m-%d %H:%M:%S")),
                    "domain": domain,
                    "host": host,
                    "url": url,
                    "agent": ua,
                    "bidder": segs[BIDDER],
                    "pushid": push_id,
                    "lacci": "",
                    "show": 0,
                    "click": 0,
                    "price": float(segs[PRICE]),
                }
            except IndexError as ie:
                logging.error(ie.message)
                pass
            logging.debug(show_detail[push_id])

    elif segs[LOG_KEY] == "rtb_show" and segs[PUSHID] in show_detail:
        if len(segs) < 12:
            logging.info("wrong show log: " + line)
            return
        show_detail[segs[PUSHID]]["show"] = 1

    elif segs[LOG_KEY] == "rtb_click" and segs[PUSHID] in show_detail:
        if len(segs) < 12:
            logging.info("wrong click log: " + line)
            return
        show_detail[segs[PUSHID]]["click"] = 1
        mutex.acquire()
        logging.info("click acquired mutex")
        try:
            flush_detail[segs[PUSHID]] = show_detail.pop(segs[PUSHID])
        except KeyError as ke:
            logging.error(ke.message)
            pass
        finally:
            mutex.release()
            logging.info("click released mutex")


if __name__ == '__main__':
    log_file_name = "log_stats_%s.log" % time.strftime("%Y-%m-%d")
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
    # parser.add_option("-s", "--server", dest="server",
    #                   help="The server address of the Elasticsearch server, for example http://user:password@192.168.56.103:9200")
    parser.add_option("-d", "--directory", dest="directory", help="The directory name")
    parser.add_option("-t", "--day", dest="day", help="The day of log")
    # parser.add_option("-f", "--files", dest="files", action="append",
    #                   help="The list of the file name, this option could be specified several times")

    options, args = parser.parse_args()
    host = options.host
    port = options.port
    user = options.user
    password = options.password
    directory = options.directory
    day = options.day

    if host is None or port is None or user is None or password is None or directory is None or day is None:
        parser.print_help()
        sys.exit(0)

    load_domain_suffix()
    ad_map = DbUtil.get_ad_info()
    logging.info("read ad info finished, length: %d" % len(ad_map))
    city_provice_map = DbUtil.get_city_info()
    logging.info("read city province info finished, length: %d" % len(city_provice_map))

    directory = directory.rstrip(os.sep)

    t = threading.Thread(target=timer_func, args=(30,))
    t.start()

    t2 = threading.Thread(target=flush_func, args=(30, host, port, user, password))
    t2.start()

    for hour in range(0, 24, 1):
        for minute in range(0, 60, 1):
            file_name = directory + os.sep + day + os.sep + "rtb_log_crit_%s%02d%02d.log" % (day, hour, minute)
            logging.debug("parse file: %s" % file_name)
            if os.path.exists(file_name):
                with open(file_name, mode='r') as fd:
                    for line in fd:
                        parse_line(line)
                logging.info("finished parse file: %s" % file_name)
            else:
                logging.info("%s not exists" % file_name)

    logging.info("parse finished")
    _FIN = 1
    t.join()
    t2.join()

    logging.warning("parse_error_num: %d, bulk_failed_num: %d, pushid_dup_num: %d, userid_null_num: %d" %
                    (parse_error_num, bulk_failed_num, pushid_dup_num, userid_null_num))
    time.sleep(3600)

