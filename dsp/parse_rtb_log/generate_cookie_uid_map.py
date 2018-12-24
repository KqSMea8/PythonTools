#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: generate_cookie_uid_map.py
@time: 20/12/2017 12:57
"""

import glob
import os
import sys
import time
import logging
from optparse import OptionParser

"""
这个脚本用于解析bidder日志，分析日志中cookie和uid的映射关系
"""

no_uid_number = 0    # 没有cookie的日志数量


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="generate_cookie_uid_map.log",
                        filemode="a")


def generate_cookie_uid_map(log_path):
    global no_uid_number
    cookie_uid_map = dict()
    glob_pattern = log_path
    if os.path.isfile(log_path):
        pass
    elif not log_path.endswith(os.path.sep):
        glob_pattern += os.path.sep + '*.log'
    else:
        glob_pattern += '*.log'

    for filename in glob.iglob(glob_pattern):
        with open(filename, mode='r') as fd:
            for line in fd:
                segs = [seg.strip() for seg in line.strip().split("\1")]
                if len(segs) >= 40 and segs[0] == "rtb_creative" or segs[0] == 'rtb_noAd':
                    try:
                        cookie = segs[5]
                        uid = segs[38]
                        if cookie is None or len(cookie) == 0:
                            no_cookie_number += 1
                            continue

                        if cookie in cookie_uid_map:
                            cookie_uid_map[cookie].add(uid)
                        else:
                            uid_set = set()
                            uid_set.add(uid)
                            cookie_uid_map[cookie] = uid_set
                    except IndexError:
                        logging.error(line)
                        continue

    return cookie_uid_map


if __name__ == '__main__':
    init_logging()
    logging.info(sys.argv)

    parser = OptionParser()
    parser.add_option('-l', '--log-dir', dest='logdir', help='The directory name of the log file')
    parser.add_option("-o", "--out-file", dest="outfile", help="The file name of the store duplicate uid")

    options,args = parser.parse_args()
    log_dir_name = options.logdir
    out_file_name = options.outfile

    if log_dir_name is None or out_file_name is None:
        parser.print_help()
        sys.exit(0)

    logging.info("begin generate_cookie_uid_map: %s" % time.asctime())
    cookie_uid_map = generate_cookie_uid_map(log_dir_name)
    logging.info("end generate_cookie_uid_map: %s" % time.asctime())
    logging.info('no_cookie_number: %d' % no_uid_number)
    duplicate_cookie_number = 0
    single_cookie_number = 0
    with open(out_file_name, mode='w') as out:
        for cookie in cookie_uid_map:
            if len(cookie_uid_map[cookie]) > 1:
                duplicate_cookie_number += 1
                for uid in cookie_uid_map[cookie]:
                    out.write("%s,%s\n" % (cookie, uid))
            else:
                single_cookie_number += 1
                print(cookie, cookie_uid_map[cookie].pop())

    logging.info('duplicate_cookie_number: %d' % duplicate_cookie_number)
    logging.info('single_cookie_number: %d' % single_cookie_number)
    logging.info("begin flush file: %s" % time.asctime())
